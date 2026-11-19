// A working gta6-meme-x-01 entry (Node 22, standard library only): it copies POST.json and
// meme.png from the repository root to /output/, where the gate reads them. The entry is the
// post itself: an AI agent made a GTA 6 meme, it is posted on X from a public account with
// make.fun (a link or written out) and/or a tag of @makefunai and a play code in its text,
// POST.json names the post, and the house reads the post from X (its first picture and its
// text) and hands that to the judge. The posted picture is byte-identical to the committed
// meme.png. Nothing this program writes about the post is judged.
//
// The POST.json this repository ships holds a placeholder address, so the gate refuses it as
// it stands (valid 0). Replace it with the post's address before submitting.
//
// The meme itself is rendered at build time by draw_meme.py (PIL, Anton font, make.fun
// ghost from assets/); main.ts only copies the finished files, so its two runs are
// byte-identical. No network, no clock, no files outside the repository.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
for (const file of ['POST.json', 'meme.png']) {
  try {
    copyFileSync(join(BOT_DIR, file), join(OUTPUT_DIR, file));
  } catch (err) {
    console.error(`${file} could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
    process.exit(1);
  }
}
