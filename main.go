// harbor: scaffold a meta repo.
package main

import (
	"bufio"
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"runtime"
	"strings"
)

var slugRe = regexp.MustCompile(`^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$`)

const template = "gh:kbhatiya999/harbor"

var in = bufio.NewReader(os.Stdin)

func fail(msg string) {
	fmt.Fprintln(os.Stderr, msg)
	os.Exit(1)
}

func ask(label, def string) string {
	hint := ""
	if def != "" {
		hint = " [" + def + "]"
	}
	fmt.Printf("%s%s: ", label, hint)
	line, err := in.ReadString('\n')
	if err != nil && line == "" {
		os.Exit(1)
	}
	if line = strings.TrimSpace(line); line != "" {
		return line
	}
	return def
}

func have(cmd string) bool {
	_, err := exec.LookPath(cmd)
	return err == nil
}

func step(title, dir string, args ...string) {
	fmt.Printf("▸ %s… ", title)
	var buf bytes.Buffer
	cmd := exec.Command(args[0], args[1:]...)
	cmd.Dir, cmd.Stdout, cmd.Stderr = dir, &buf, &buf
	if err := cmd.Run(); err != nil {
		fmt.Println("✗")
		out := strings.TrimSpace(buf.String())
		if out == "" {
			out = err.Error()
		}
		fail(out)
	}
	fmt.Println("✓")
}

func firstAvailable(options [][]string) []string {
	for _, o := range options {
		if have(o[0]) {
			return o
		}
	}
	return nil
}

func installCopier() {
	cmd := firstAvailable([][]string{
		{"uv", "tool", "install", "copier"},
		{"pipx", "install", "copier"},
		{"pip3", "install", "--user", "copier"},
		{"pip", "install", "--user", "copier"},
	})
	if cmd == nil {
		fail("No Python package manager found. Install copier: https://copier.readthedocs.io")
	}
	step("Installing copier", "", cmd...)
}

func installMise() {
	cmd := []string{"sh", "-c", "curl -fsSL https://mise.run | sh"}
	if runtime.GOOS == "windows" {
		cmd = firstAvailable([][]string{
			{"winget", "install", "--id", "jdx.mise", "--silent"},
			{"scoop", "install", "mise"},
		})
		if cmd == nil {
			fail("Install mise manually: https://mise.jdx.dev/getting-started.html")
		}
	}
	step("Installing mise", "", cmd...)
}

func main() {
	fmt.Println("harbor setup: create a meta repo (mani · mise · copier)")
	fmt.Println()

	slug := ask("GitHub slug (owner/repo)", "")
	for !slugRe.MatchString(slug) {
		fmt.Println("  must be owner/repo, e.g. kbhatiya999/my-meta")
		slug = ask("GitHub slug (owner/repo)", "")
	}
	repo := slug[strings.LastIndex(slug, "/")+1:]

	desc := ask("Description", repo+" meta repo")
	fnox := strings.HasPrefix(strings.ToLower(ask("Include fnox? (y/n)", "y")), "y")
	dest := ask("Create in", "./"+repo)
	fmt.Println()

	if !have("copier") {
		installCopier()
	}
	step("Scaffolding repo", "", "copier", "copy", template, dest,
		"--data", "github_slug="+slug,
		"--data", "description="+desc,
		"--data", fmt.Sprintf("use_fnox=%t", fnox),
		"--defaults", "--overwrite")

	if !have("mise") {
		installMise()
	}
	step("mise install", dest, "mise", "install")
	step("mise run sync", dest, "mise", "run", "sync")

	fmt.Printf(`
Done! Meta repo %s is ready.

  cd %s
  mise run hello    # verify task runner
  mise run status   # git status across sub-repos
  mise run pull     # pull all sub-repos

Pull future template updates with: copier update
`, repo, dest)
}
