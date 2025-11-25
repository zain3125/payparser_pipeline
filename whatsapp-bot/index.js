const fs = require('fs');
const path = require('path');
const axios = require('axios');
const qrcode = require('qrcode-terminal');
const { Client, LocalAuth } = require('whatsapp-web.js');

const AIRFLOW_API_BASE = 'http://localhost:8080/api/v1/variables';
const AIRFLOW_USERNAME = 'airflow';
const AIRFLOW_PASSWORD = 'airflow';

const now = new Date();
const todayDate = now.toLocaleDateString('en-US', { day: '2-digit', month: 'long' });

console.log(`📥 Fetching ${todayDate} images`);

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
        console.error(`❌ Failed to fetch variable "${key}":`, error.message);
        return null;
    }
}

function sanitizeFileName(text) {
    return text
        .replace(/[^\u0600-\u06FF\w\s\-_()]/g, ' ')
        .replace(/\s+/g, ' ')
        .substring(0, 50)
        .trim();
}

async function startBot() {
    const groupName = await getAirflowVariable('group_name');
    const authorNamesRaw = await getAirflowVariable('author_names');

    let authorNames = {};
    try {
        authorNames = JSON.parse(authorNamesRaw || '{}');
    } catch (e) {
        console.error('❌ Failed to parse author_names:', e.message);
    }

    const client = new Client({
        authStrategy: new LocalAuth({
            dataPath: path.join(__dirname, 'auth', 'session')
        }),
        puppeteer: {
            executablePath: '/snap/bin/brave',
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                `--user-data-dir=${path.join(__dirname, 'chrome_data')}`
            ]
        }
    });

    client.on('qr', qr => qrcode.generate(qr, { small: true }));
    
    client.on('auth_failure', msg => {
        console.error('❌ Authentication failed:', msg);
    });

    client.on('disconnected', reason => {
        console.error('❌ Client was disconnected:', reason);
    });

    client.on('loading_screen', (percent, message) => {
        console.log('⏳ Loading...', percent, message);
    });

    client.on('ready', async () => {
        console.log('✅ WhatsApp is ready!');

        const chats = await client.getChats();
        const group = chats.find(chat => chat.isGroup && chat.name === groupName);

        if (!group) {
            console.log('❌ Group not found!');
            return;
        }
    
        const now = new Date();
        const todayDate = now.toLocaleDateString('en-US', { day: '2-digit', month: 'long' });

        console.log(`📥 Fetching ${todayDate} images from group: ${group.name}`);

        const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
        const endOfRange = now;

        const messages = await group.fetchMessages({ limit: 500 });

        for (const msg of messages) {
            const msgDate = new Date(msg.timestamp * 1000);
            if (msg.hasMedia && msgDate >= startOfToday && msgDate <= endOfRange) {
                try {
                    const media = await msg.downloadMedia();
                    const ext = media.mimetype.split('/')[1];
                    const author = msg.author || null;
                    if (!author) continue;
                    const authorName = authorNames[author] || author;

                    const folderPath = path.join(__dirname, '..', 'airflow', 'shared', 'downloads', authorName);
                    if (!fs.existsSync(folderPath)) fs.mkdirSync(folderPath, { recursive: true });

                    let captionPart = '';
                    if (msg.body) {
                        const clean = sanitizeFileName(msg.body);
                        captionPart = `(${clean})`;
                    }

                    const filename = `photo_${Date.now()}${captionPart}.${ext}`;
                    const filepath = path.join(folderPath, filename);
                    fs.writeFileSync(filepath, media.data, { encoding: 'base64' });

                    console.log(`✅ Saved: ${filename} from ${authorName}`);
                } catch (err) {
                    console.error('❌ Error saving media:', err.message);
                }
            }
        }

        console.log('✅ Done. Exiting...');
        console.log('***********************************');
        process.exit(0);
    });

    client.initialize({ timeout: 60000 });
}

startBot();
