# Vercel Deployment Guide

This guide will help you deploy your Ad-Creative Insight Pipeline to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. Your Supabase credentials
3. Git repository with your code

## Deployment Steps

### 1. Environment Variables

In your Vercel dashboard, add these environment variables:

**Required:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Your Supabase service role key
- `SUPABASE_ANON_KEY` - Your Supabase anon key
- `SECRET_KEY` - A random secret key for Flask sessions

**Optional (for pipeline functionality):**
- `OPENAI_API_KEY` - Your OpenAI API key
- `REDDIT_CLIENT_ID` - Reddit API client ID
- `REDDIT_CLIENT_SECRET` - Reddit API client secret
- `REDDIT_USER_AGENT` - Reddit API user agent
- `REDDIT_USERNAME` - Reddit username
- `REDDIT_PASSWORD` - Reddit password

### 2. Deploy to Vercel

#### Option A: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow the prompts to link your project
```

#### Option B: Deploy via GitHub Integration
1. Push your code to GitHub
2. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
3. Click "New Project"
4. Import your GitHub repository
5. Vercel will automatically detect the configuration

### 3. Configuration Files

The project includes these Vercel-specific files:

- `vercel.json` - Vercel deployment configuration
- `api/index.py` - Vercel serverless function entry point
- `.vercelignore` - Files to exclude from deployment

### 4. Features Available on Vercel

✅ **Working Features:**
- Insights Management - View and manage existing insights
- Database connectivity - Connect to your Supabase database
- Web interface - Full web UI for managing insights
- API endpoints - All REST API endpoints work

❌ **Limited Features:**
- Pipeline execution - Not available in serverless environment
- Real-time updates - SocketIO disabled for serverless compatibility
- Long-running processes - Use external services for data processing

### 5. Post-Deployment

After deployment:

1. Visit your Vercel URL
2. Test the `/health` endpoint to verify deployment
3. Check the Insights Management page to verify database connectivity
4. Add environment variables if any features aren't working

### 6. Troubleshooting

**Common Issues:**

1. **Database Connection Errors**
   - Verify your Supabase credentials in environment variables
   - Check that your Supabase project is accessible

2. **Import Errors**
   - The app gracefully handles missing dependencies
   - Mock data will be shown if database isn't accessible

3. **Template Not Found**
   - Ensure the `web_frontend/templates/` directory is included
   - Check that template files exist: `index.html`, `insights.html`, `config.html`

### 7. Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env file
cp .env.example .env
# Edit .env with your credentials

# Run the Flask app
python web_frontend/app.py
```

### 8. Scaling Considerations

For production use:

- Use Vercel Pro for better performance limits
- Consider using Vercel Edge Functions for better global performance
- Set up monitoring and logging
- Use a CDN for static assets

## Support

If you encounter issues:

1. Check Vercel function logs in the dashboard
2. Verify environment variables are set correctly
3. Test database connectivity using the `/health` endpoint
4. Check the browser console for frontend errors