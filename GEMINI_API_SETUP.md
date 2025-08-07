# 🔑 How to Get Your Free Gemini API Key

## Quick Start Guide

To enable AI-powered summaries in your newsletter generator, you'll need a free Google Gemini API key.

### Step 1: Get Your Free API Key

1. **Visit Google AI Studio**: Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

2. **Sign In**: Use your Google account to sign in

3. **Create API Key**: Click the "Create API key" button

4. **Copy the Key**: Copy the generated API key (it starts with "AIza...")

### Step 2: Add API Key to Your Project

**Option 1: Add to .env file (Recommended)**
1. Open the `.env` file in your project root
2. Find the line: `GEMINI_API_KEY=`
3. Add your key: `GEMINI_API_KEY=AIzaSyC...your-key-here`
4. Save the file

**Option 2: Enter in Web Interface**
1. Run the web interface
2. Enter your API key in the text input field
3. The system will use it immediately

### Step 3: Restart and Test

1. Restart the web interface if it's running
2. You should see "✅ Gemini API key detected - Full AI features available"
3. Generate a newsletter to test the AI features

## Free Tier Limits

The Gemini API free tier is very generous:

- **15 requests per minute**
- **1 million tokens per minute**  
- **1,500 requests per day**

This is more than enough for generating multiple newsletters per day!

## Example API Key Format

Your API key will look like this:
```
AIzaSyC-1234567890abcdefghijklmnopqrstuvwxyz
```

## Troubleshooting

**"API key not found" error:**
- Check that you copied the entire key
- Make sure there are no extra spaces
- Verify the key starts with "AIza"

**"Quota exceeded" error:**
- You've hit the daily limit (1,500 requests)
- Wait until tomorrow or upgrade to a paid plan

**"Invalid API key" error:**
- Double-check you copied the key correctly
- Make sure you're using a Gemini API key, not other Google service keys

## Security Notes

- Keep your API key private
- Don't share it in public repositories
- The `.env` file is already in `.gitignore` to protect your key
- You can regenerate your key anytime in Google AI Studio

## Ready to Go!

Once you have your API key set up, you'll get:
- ✅ Real AI-powered article summaries
- ✅ Intelligent key point extraction
- ✅ Relevant quote identification
- ✅ Personalized newsletter introductions

The AI will analyze each article and create professional, concise summaries tailored to your interests!
