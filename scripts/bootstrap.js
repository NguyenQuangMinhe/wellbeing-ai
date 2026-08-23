import { execSync } from 'child_process';
import { existsSync, copyFileSync } from 'fs';

function run(cmd) {
  console.log(`\n> ${cmd}`);
  execSync(cmd, { stdio: 'inherit' });
}

console.log('Bootstrapping wellbeing-ai...\n');

// 1. Install all workspace dependencies
run('pnpm install');

// 2. Create root .env from .env.example if missing
if (!existsSync('.env')) {
  if (existsSync('.env.example')) {
    copyFileSync('.env.example', '.env');
    console.log('\nCreated .env from .env.example — fill in any local values.');
  } else {
    console.log('\nNo .env.example found — skipping .env creation.');
  }
} else {
  console.log('\n.env already exists — leaving it as is.');
}

// 3. Install git hooks (only if lefthook is set up)
try {
  run('pnpm exec lefthook install');
} catch {
  console.log('\nLefthook not installed yet — skipping git hooks. Run `pnpm add -D -w lefthook` to add it later.');
}

console.log('\nBootstrap complete. Run `pnpm dev` to start the frontend.');