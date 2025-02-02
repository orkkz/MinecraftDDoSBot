const mineflayer = require('mineflayer');

if (process.argv.length < 5) {
  console.log("Usage: node bot.js <botUsername> <serverAddress> <duration>");
  process.exit(1);
}
const botUsername = process.argv[2];
const serverAddress = process.argv[3];
const duration = parseInt(process.argv[4], 10);
const [host, port] = serverAddress.split(':');
const serverPort = port ? parseInt(port, 10) : 25565;
const bot = mineflayer.createBot({
  host: host,
  port: serverPort,
  username: botUsername,
  version: '1.18.2'
});
bot.on('spawn', () => {
  console.log(`Bot ${botUsername} has spawned on ${serverAddress}`);
  const chineseChars = "你好我是你的朋友服务器崩溃攻击";
  const chatInterval = setInterval(() => {
    const msg = Array.from({ length: Math.floor(Math.random() * 5) + 5 }, () => chineseChars.charAt(Math.floor(Math.random() * chineseChars.length))).join('');
    bot.chat(msg);
  }, 1000);
  bot.on('windowOpen', (window) => {
    if (window.title === 'Inventory') {
      for (let i = 0; i < 36; i++) {
        const slot = window.slots[i];
        if (slot && slot.count > 0) {
          bot.tossStack(slot);
        }
      }
    }
  });
  setTimeout(() => {
    clearInterval(chatInterval);
    bot.quit(); // Disconnect the bot
    console.log(`Bot ${botUsername} disconnected after ${duration} seconds.`);
  }, duration * 1000);
});

bot.on('error', (err) => {
  console.log('Error:', err);
});

bot.on('end', () => {
  console.log('Bot disconnected');
});
