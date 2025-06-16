//import necessary libraries
const venom = require('venom-bot');
const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Define constants for Airflow API
const AIRFLOW_API_BASE = 'http://localhost:8080/api/v1/variables';
const AIRFLOW_USERNAME = 'airflow';
const AIRFLOW_PASSWORD = 'airflow';

// Function to get Airflow variable
async function getAirflowVariable(key) {
  try {
    const response = await axios.get(`${AIRFLOW_API_BASE}/${key}`, {
      auth: {
        username: AIRFLOW_USERNAME,
        password: AIRFLOW_PASSWORD
      }
    });
    return response.data.value;
  } catch (error) {
    console.error(`Failed to fetch variable "${key}":`, error.message);
    return null;
  }
}

// Function to sanitize file names
function sanitizeFileName(text) {
  return text
    .replace(/[^\u0600-\u06FF\w\s\-_()]/g, ' ')
    .replace(/\s+/g, ' ')
    .substring(0, 50)
    .trim();
}

// Main function
async function startBot() {
  const groupName = await getAirflowVariable('group_name');
  // Print group name
  console.log("Group Name:", groupName);
  const authorNamesRaw = await getAirflowVariable('author_names');

  let authorNames = {};
  try {
    authorNames = JSON.parse(authorNamesRaw || '{}');
  } catch (e) {
    console.error('Failed to parse author_names variable:', e.message);
  }

  venom
    .create({ session: 'session-name' })
    .then(client => start(client, groupName, authorNames))
    .catch(err => console.log('Error creating venom session:', err));
}

// Start the bot
function start(client, groupName, authorNames) {
  client.onMessage(async (message) => {
    const isFromGroup =
      message.isGroupMsg === true &&
      message.groupInfo &&
      message.groupInfo.name === groupName;

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
        const authorFolder = path.join(__dirname, '..', 'airflow', 'shared', 'downloads', authorName);

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

startBot();
