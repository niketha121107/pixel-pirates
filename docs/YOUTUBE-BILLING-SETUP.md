# YouTube API Billing Setup Guide

This guide explains how to enable billing on Google Cloud for unlimited YouTube API quota in the Pixel Pirates learning platform.

## 🎯 Overview

The Pixel Pirates platform uses a **hybrid video delivery system**:

- **Primary**: Stored database videos (3 videos per topic) - **Always available, no API calls**
- **Secondary**: Fresh YouTube videos on-demand - **Requires billing enabled**

### Current Status
- ✅ **Stored Videos**: 200 topics × 3 videos = **600 videos ready**
- ⏳ **Fresh Videos**: Requires billing enablement

---

## 📋 Prerequisites

1. **Google Account** (same account that created your YouTube API key)
2. **Credit Card** (for billing setup)
3. **YouTube API Key**: `AIzaSyBOPk5XIQIVFI_C8awnv3GPPqGFQBAvygo`

---

## 🔧 Step-by-Step Setup

### **Step 1: Go to Google Cloud Console**

1. Open: https://console.cloud.google.com/
2. Sign in with your Google account
3. You should see your project in the top dropdown

### **Step 2: Identify Your Project**

1. Click the **Project Dropdown** (top left)
2. Look for your project name
3. Note the **Project ID** (format: `project-12345678`)

### **Step 3: Link a Billing Account**

1. In the left sidebar, click **Billing**
2. You should see:
   - If already linked: Blue checkmark ✅
   - If not linked: Option to **"Link a billing account"**

### **Step 4: Create/Select Billing Account**

If you don't have a billing account:

1. Click **"Create Billing Account"**
2. Fill in your information:
   - **Name**: Your name or organization
   - **Country**: Your location
   - **Address**: Your address
3. Click **Create**

### **Step 5: Add Payment Method**

1. Go to **Billing** → **Overview**
2. Click **"Manage Billing Accounts"**
3. Click your billing account
4. Go to **Payment Method**
5. Click **"Add Payment Method"**
6. Enter credit card details:
   - Card Number
   - Expiry Date
   - CVC
   - Billing Address

### **Step 6: Verify YouTube API is Enabled**

1. Go to **APIs & Services** → **Enabled APIs & Services**
2. Look for **"YouTube Data API v3"**
3. If not listed, search and enable it

### **Step 7: Set Billing Alerts (Recommended)**

1. Go to **Billing** → **Budgets & Alerts**
2. Click **"Create Budget"**
3. Configure:
   - **Scope**: Select your project
   - **Amount**: $20/month (example)
   - **Alert Email**: Your email
4. Save

---

## 💰 Cost Estimation

### Pricing

| Operation | Cost | Unit |
|-----------|------|------|
| Video search | $1.50 | per 1,000 queries |
| Video list | $1.50 | per 1,000 queries |
| Search list | $1.50 | per 1,000 queries |

### Example Usage

- **100 fresh video requests/month**: ~$0.15
- **1,000 fresh video requests/month**: ~$1.50
- **10,000 fresh video requests/month**: ~$15.00

### Sample Budgets

| Usage Level | Monthly Cost | Queries/Day |
|------------|-------------|-----------|
| **Light** (Student/hobby) | $0-2 | 0-100 |
| **Medium** (Growing platform) | $5-10 | 100-300 |
| **Heavy** (Production app) | $15-50 | 300-1000+ |

---

## ✅ Verification Steps

### **After Enabling Billing:**

1. **Check API Status**
   - Go to **APIs & Services** → **YouTube Data API v3**
   - Click **Quotas**
   - Should show daily quota as **1,000,000 requests**
   - Free tier shows **10,000 requests**

2. **Test Fresh Videos Button**
   - Login to Pixel Pirates
   - Open any topic
   - Click **"Get Fresh Videos"** button below the video
   - Should load 3 fresh videos from YouTube

3. **Monitor Quota Usage**
   - Go to **APIs & Services** → **Dashboard**
   - Check **YouTube Data API v3** usage graph
   - Should show queries when fetching fresh videos

### **Expected Result**

```
✅ Stored video loads instantly (primary)
✅ "Get Fresh Videos" button works (secondary)
✅ Fresh videos display with YouTube content
✅ No quota exhaustion errors
```

---

## 🔍 Troubleshooting

### **Issue: "Billing not linked" error**

**Solution:**
1. Ensure billing account is linked to your project
2. Check that payment method is valid
3. Wait 15-30 minutes for changes to propagate

### **Issue: Fresh videos still not working**

**Solution:**
1. Refresh your browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
2. Check that YouTube Data API v3 is enabled
3. Verify API key in `.env` file matches Google Cloud project
4. Check browser console for error messages

### **Issue: "Quota exceeded" error persists**

**Solution:**
1. Go to Google Cloud Console
2. Navigate to **APIs & Services** → **Credentials**
3. Verify the API key restrictions:
   - Should have **no IP restrictions** (or whitelist your server)
   - Should allow **YouTube Data API v3**
4. Try generating a new API key if old one has restrictions

### **Issue: Want to disable fresh videos?**

Simply avoid clicking "Get Fresh Videos" button - stored videos will always work!

---

## 📊 Monitoring & Management

### **View API Usage**

1. **Dashboard**: APIs & Services → Dashboard → YouTube Data API v3
2. **Detailed Logs**: Logging → Logs Viewer → Filter by API name
3. **Billing Reports**: Billing → Reports

### **Set Up Alerts**

**Via Billing:**
- Billing → Budgets & Alerts → Create alert when spending reaches threshold

**Via API Quotas:**
- APIs & Services → Quotas → Set threshold alerts

### **Disable/Re-enable**

**To disable fresh videos feature:**
- Backend will fall back to stored videos automatically
- Restart backend: `python main.py`

---

## 🎓 Best Practices

1. **Always set billing alerts** - Avoid surprise charges
2. **Monitor quota usage** - Adjust budget if needed
3. **Cache results** - Reuse fresh video results to minimize quota usage
4. **Use stored videos as priority** - They're instant and free
5. **Implement rate limiting** - Limit fresh video requests per user/day

---

## 📚 Additional Resources

- **Google Cloud Console**: https://console.cloud.google.com/
- **YouTube API Documentation**: https://developers.google.com/youtube/v3
- **Quotas & Limits**: https://developers.google.com/youtube/quotas
- **Billing Documentation**: https://cloud.google.com/billing/docs

---

## ❓ FAQ

### **Q: Will this cost money immediately?**
A: No. Free tier includes 10,000 quota units/day. Most small-scale usage fits within free tier. When you exceed that, you'll need billing.

### **Q: What if I enable billing but don't use fresh videos?**
A: No charge. You only pay for what you use. Stored videos are always free.

### **Q: Can I disable billing later?**
A: Yes. Any time. Fresh videos will stop working, but stored videos continue working.

### **Q: Will my card be charged automatically?**
A: Only if you exceed free tier AND have billing enabled. Check your billing alerts to get notifications.

### **Q: How do I see what I've been charged?**
A: Check **Billing** → **Transactions** to see all charges.

---

## 🚀 Next Steps

1. ✅ Complete billing setup above
2. ✅ Test fresh videos button in the app
3. ✅ Set up billing alerts
4. ✅ Monitor usage in dashboard
5. ✅ Enjoy unlimited fresh YouTube content!

---

**Last Updated**: March 21, 2026  
**Status**: Active - Billing setup complete ✅
