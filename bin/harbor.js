#!/usr/bin/env node
// harbor: scaffold a meta repo.
const readline = require("node:readline/promises");
const { spawnSync } = require("node:child_process");

const SLUG_RE = /^[A-Za-z0-9-]+\/[A-Za-z0-9._-]+$/;
const TEMPLATE = "gh:kbhatiya999/harbor";

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const lines = rl[Symbol.asyncIterator]();

function fail(msg) {
  console.error(msg);
  process.exit(1);
}

async function ask(label, def = "") {
  const hint = def ? ` [${def}]` : "";
  process.stdout.write(`${label}${hint}: `);
  const { value, done } = await lines.next();
  if (done) process.exit(1); // stdin closed (ctrl+d) before we finished
  return value.trim() || def;
}

function have(cmd) {
  const probe = process.platform === "win32" ? "where" : "which";
  return spawnSync(probe, [cmd], { stdio: "ignore" }).status === 0;
}

function step(title, args, cwd) {
  process.stdout.write(`▸ ${title}… `);
  const r = spawnSync(args[0], args.slice(1), { cwd, encoding: "utf8" });
  const ok = r.status === 0;
  console.log(ok ? "✓" : "✗");
  if (!ok) fail((r.stderr || r.stdout || (r.error && r.error.message) || "").trim());
}

const firstAvailable = (options) => options.find((o) => have(o[0]));

function installCopier() {
  const cmd = firstAvailable([
    ["uv", "tool", "install", "copier"],
    ["pipx", "install", "copier"],
    ["pip3", "install", "--user", "copier"],
    ["pip", "install", "--user", "copier"],
  ]);
  if (!cmd) fail("No Python package manager found. Install copier: https://copier.readthedocs.io");
  step("Installing copier", cmd);
}

function installMise() {
  let cmd = ["sh", "-c", "curl -fsSL https://mise.run | sh"];
  if (process.platform === "win32") {
    cmd = firstAvailable([
      ["winget", "install", "--id", "jdx.mise", "--silent"],
      ["scoop", "install", "mise"],
    ]);
    if (!cmd) fail("Install mise manually: https://mise.jdx.dev/getting-started.html");
  }
  step("Installing mise", cmd);
}

async function main() {
  console.log("harbor setup: create a meta repo (mani · mise · copier)\n");

  let slug = await ask("GitHub slug (owner/repo)");
  while (!SLUG_RE.test(slug)) {
    console.log("  must be owner/repo, e.g. kbhatiya999/my-meta");
    slug = await ask("GitHub slug (owner/repo)");
  }
  const repo = slug.split("/").pop();

  const desc = await ask("Description", `${repo} meta repo`);
  const fnox = (await ask("Include fnox? (y/n)", "y")).toLowerCase().startsWith("y");
  const dest = await ask("Create in", `./${repo}`);
  rl.close();
  console.log();

  if (!have("copier")) installCopier();
  step("Scaffolding repo", [
    "copier", "copy", TEMPLATE, dest,
    "--data", `github_slug=${slug}`,
    "--data", `description=${desc}`,
    "--data", `use_fnox=${fnox}`,
    "--defaults", "--overwrite",
  ]);

  if (!have("mise")) installMise();
  step("mise install", ["mise", "install"], dest);
  step("mise run sync", ["mise", "run", "sync"], dest);

  console.log(`
Done! Meta repo ${repo} is ready.

  cd ${dest}
  mise run hello    # verify task runner
  mise run status   # git status across sub-repos
  mise run pull     # pull all sub-repos

Pull future template updates with: copier update`);
}

main();
