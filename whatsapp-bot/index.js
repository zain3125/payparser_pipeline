const venom = require('venom-bot');
const fs = require('fs');
const path = require('path');

// Replace with actual author IDs and names as needed
const authorNames = {};


function sanitizeFileName(text) {
  return text
    .replace(/[^\u0600-\u06FF\w\s\-_()]/g, ' ') 
    .replace(/\s+/g, ' ')
    .substring(0, 50)
    .trim();
}

venom
  .create({
    session: 'session-name'
  })
  .then(client => start(client))
  .catch(err => console.log('Error creating venom session:', err));

function start(client) {
  client.onMessage(async (message) => {
    const isFromGroup = message.isGroupMsg === true && message.groupInfo && message.groupInfo.name === 'فودافون كاش 💸';

    if (
      message.mimetype &&
      message.mimetype.startsWith('image/') &&
      isFromGroup
    ) {
      try {
        const buffer = await client.decryptFile(message);
        const mediaExtension = message.mimetype.split('/')[1];

        const author = message.author || message.from;
        const authorName = authorNames[author] || author;
        const authorFolder = path.join(__dirname, 'downloads', authorName);

        if (!fs.existsSync(authorFolder)) {
          fs.mkdirSync(authorFolder, { recursive: true });
        }

        let captionPart = '';
        if (message.caption) {
          const sanitizedCaption = sanitizeFileName(message.caption);
          captionPart = `(${sanitizedCaption})`;
        }

        const fileName = `photo_${Date.now()}${captionPart}.${mediaExtension}`;
        const filePath = path.join(authorFolder, fileName);

        fs.writeFileSync(filePath, buffer);

        console.log(`Image saved: ${fileName} from author: ${authorName}`);
      } catch (error) {
        console.error('Error saving image:', error);
      }
    }
  });
}
