// 사용법:
//   node render.js                 -> frames를 ffmpeg로 인코딩해 jaapangi_video_only.mp4 생성
//   node render.js --stills 1,5,9  -> 지정 시점 정지 이미지(still_*.png) 저장
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const FPS = 30;
const OUT = path.join(__dirname, 'jaapangi_video_only.mp4');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'index.html') + '?render');
  await page.evaluate(() => window.ready);

  const grab = t => page.evaluate(t => {
    window.renderFrame(t);
    return document.getElementById('c').toDataURL('image/png').split(',')[1];
  }, t);

  const si = process.argv.indexOf('--stills');
  if (si > -1) {
    const fs = require('fs');
    for (const t of process.argv[si + 1].split(',').map(Number)) {
      fs.writeFileSync(path.join(process.argv[si + 2] || __dirname, `still_${t}.png`), Buffer.from(await grab(t), 'base64'));
    }
    await browser.close();
    return;
  }

  const duration = await page.evaluate(() => window.DURATION);
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', OUT], { stdio: ['pipe', 'ignore', 'inherit'] });
  const total = Math.round(duration * FPS);
  for (let f = 0; f < total; f++) {
    const buf = Buffer.from(await grab(f / FPS), 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 90 === 0) process.stderr.write(`frame ${f}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('done:', OUT);
})();
