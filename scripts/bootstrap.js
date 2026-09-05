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
if (!existsSync('frontend/.env.local')) {
  if (existsSync('frontend/.env.example')) {
    copyFileSync('frontend/.env.example', 'frontend/.env.local');
    console.log('\nCreated frontend/.env.local from frontend/.env.example — fill in any local values.');
  }
}

// 3. Install git hooks (only if lefthook is set up)
try {
  run('pnpm exec lefthook install');
} catch {
  console.log('\nLefthook not installed yet — skipping git hooks. Run `pnpm add -D -w lefthook` to add it later.');
}

// 4. Set up backend virtual environment and install dependencies
if (existsSync('backend')) {
  if (!existsSync('backend/venv')) {
    console.log('\nSetting up backend virtual environment...');
    run('python -m venv backend/venv');
  }

  const isWindows = process.platform === 'win32';
  const pipPath = isWindows ? 'backend\\venv\\Scripts\\pip.exe' : 'backend/venv/bin/pip';

  if (existsSync('backend/requirements.txt')) {
    run(`${pipPath} install -r backend/requirements.txt`);
  } else {
    console.log('\nbackend/requirements.txt not found — skipping backend dependency install.');
  }

  if (!existsSync('backend/.env') && existsSync('backend/.env.example')) {
    copyFileSync('backend/.env.example', 'backend/.env');
    console.log('Created backend/.env from backend/.env.example');
  }
} else {
  console.log('\nNo backend/ folder found yet — skipping backend setup.');
}

console.log('\nBootstrap complete. Run `pnpm dev` for the frontend, `pnpm run backend:dev` for the backend.');