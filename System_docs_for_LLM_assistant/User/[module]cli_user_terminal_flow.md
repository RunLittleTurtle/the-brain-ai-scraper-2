# CLI User Flow Examples

## Table of Contents

1. [Basic Natural Language Scrape Flow](#1-basic-natural-language-scrape-flow)
2. [Error Recovery and Selector Adjustment Flow](#2-error-recovery-and-selector-adjustment-flow)
3. [Field Adjustment and Refinement Flow](#3-field-adjustment-and-refinement-flow)
4. [Anti-Bot Protection Flow](#4-anti-bot-protection-flow)
5. [Multi-Page Scraping Flow](#5-multi-page-scraping-flow)
6. [Structured Command Flow](#6-structured-command-flow)
7. [Project Organization Flow](#7-project-organization-flow)
8. [Output Quality Improvement Flow](#8-output-quality-improvement-flow)

## 1. Basic Natural Language Scrape Flow

```
$ brain scrape "Get me the price and title from this Amazon product: https://amazon.ca/dp/B08WRBGSL2"

🧠 Analyzing request with intent_inference...

ℹ️ Intent analysis complete:
  - Target URL: https://amazon.ca/dp/B08WRBGSL2
  - Fields to extract: price, title
  - Technical requirements: JavaScript rendering required (detected Amazon domain)

📋 Confirm extraction fields:
  > ◉ price
    ◉ title
    ◯ description
    ◯ rating
    ◯ reviews
    ◯ availability
    ◯ images

Do you want to proceed with these fields? [Y/n/edit]: Y

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  1. Browser: Playwright (Reason: JavaScript rendering needed for Amazon)
  2. Parser: BeautifulSoup4 (Reason: HTML extraction for price and title)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...  [##########--------] 50%
📊 Current step: Loading page with Playwright...

🔄 Executing scrape with executor...  [####################] 100%
📊 Extracting data with BeautifulSoup...

✅ Scraping complete! Found 2 fields:
  - Price: $499.99
  - Title: Sony PlayStation 5 Console

💾 Results saved as run_123

📋 Are these results satisfactory? [Y/n/issues/more fields]: Y

📂 Project management:
  - Current project: Personal Shopping (3 runs)
  - Save this run to current project? [Y/n/change project]: Y

ℹ️ Run added to "Personal Shopping" project.
💡 Tip: Use 'brain export run_123 --format csv' to export these results
```

## 2. Error Recovery and Selector Adjustment Flow

```
$ brain scrape "Extract price from this eBay listing: https://ebay.com/itm/123456789"

🧠 Analyzing request with intent_inference...

ℹ️ Intent analysis complete:
  - Target URL: https://ebay.com/itm/123456789
  - Fields to extract: price
  - Technical requirements: JavaScript rendering required (detected eBay domain)

📋 Confirm extraction fields:
  > ◉ price
    ◯ title
    ◯ seller
    ◯ shipping
    ◯ condition

Do you want to proceed with these fields? [Y/n/edit]: Y

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  1. Browser: Playwright (Reason: JavaScript rendering needed for eBay)
  2. Parser: BeautifulSoup4 (Reason: HTML extraction for price)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...  [##############----] 70%
📊 Extracting data with BeautifulSoup...

❌ Error: Selector '.prcIsum' not found on page
This often happens when sites change their layout or use dynamic content.

💡 Diagnostic from evaluator:
  - Error type: Selector not found
  - Common causes: Site layout change, A/B testing, region-specific variant
  - Knowledge base entries: 3 similar issues found for eBay

💡 Available actions:
  1. analyze - Use evaluator to analyze page structure and find selectors
  2. retry - Retry with different selector
  3. browser - Try a different browser tool
  4. abort - Cancel this scrape

Choose an action [1-4]: 1

🔍 Running page structure analysis with scrape_analyzer...
🔄 [####----------] 20% Capturing page snapshot
🔄 [########------] 40% Identifying page elements
🔄 [############--] 60% Mapping element hierarchy
🔄 [################] 80% Searching for price patterns
🔄 [####################] 100% Generating recommendations

ℹ️ Analysis complete:
  - Found potential price selector: '.s-item__price'
  - Detected layout: "New eBay listing page format"
  - Knowledge base match: "eBay 2023 Q2 layout update"
  - Recommendation: Update selector for price

📋 Would you like to retry with the suggested selector? [Y/n]: Y

⚙️ Rebuilding pipeline with updated selectors...
🔄 [########------] 40% Updating extraction parameters
🔄 [################] 80% Reconfiguring parser settings
🔄 [####################] 100% Finalizing updated pipeline

🔄 Retrying scrape with updated selectors...  [####################] 100%

✅ Scraping complete! Found 1 field:
  - Price: $349.99

💾 Results saved as run_124

📋 Are these results satisfactory? [Y/n/issues/more fields]: Y

📂 Project management:
  - Current project: Personal Shopping (4 runs)
  - Save this run to current project? [Y/n/change project]: Y

ℹ️ Run added to "Personal Shopping" project.
💡 The system has updated its knowledge base with the new eBay price selectors.
```

## 3. Field Adjustment and Refinement Flow

```
$ brain scrape "Get product details from Walmart: https://walmart.com/ip/567890"

🧠 Analyzing request with intent_inference...

ℹ️ Intent analysis complete:
  - Target URL: https://walmart.com/ip/567890
  - Fields to extract: unspecified product details
  - Technical requirements: JavaScript rendering required (detected Walmart domain)

📋 Since you didn't specify fields, here are recommended fields:
  > ◉ price
    ◉ title
    ◯ description
    ◯ rating
    ◯ stock_status
    ◯ brand
    ◯ specifications

Do you want to proceed with these fields? [Y/n/edit]: edit

📋 Select fields to extract:
  > ◉ price
    ◉ title
    ◉ description
    ◉ rating
    ◉ stock_status
    ◯ brand
    ◯ specifications

Is this selection correct? [Y/n]: Y

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  1. Browser: Playwright (Reason: JavaScript rendering needed for Walmart)
  2. Parser: BeautifulSoup4 (Reason: HTML extraction for selected fields)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...  [####################] 100%

✅ Scraping complete! Found 5 fields:
  - Price: $24.99
  - Title: Everyday Value Bath Towel
  - Description: Soft and absorbent bath towel perfect for daily use...
  - Rating: 4.3/5 (127 reviews)
  - Stock Status: In Stock

💾 Results saved as run_125

📋 Are these results satisfactory? [Y/n/issues/more fields]: more fields

📋 Select additional fields to extract:
  > ◯ price (already extracted)
    ◯ title (already extracted)
    ◯ description (already extracted)
    ◯ rating (already extracted)
    ◯ stock_status (already extracted)
    ◉ brand
    ◉ specifications
    ◯ color_options
    ◯ shipping_info

Is this selection correct? [Y/n]: Y

⚙️ Updating pipeline for additional fields...
🔄 [########------] 40% Adding extraction parameters
🔄 [################] 80% Reconfiguring parser settings
🔄 [####################] 100% Finalizing updated pipeline

🔄 Extracting additional fields...  [####################] 100%

✅ Updated results:
  - Price: $24.99
  - Title: Everyday Value Bath Towel
  - Description: Soft and absorbent bath towel perfect for daily use...
  - Rating: 4.3/5 (127 reviews)
  - Stock Status: In Stock
  - Brand: Walmart Essentials
  - Specifications:
    * Material: 100% Cotton
    * Dimensions: 30" x 54"
    * Weight: 450 GSM
    * Country of Origin: India

💾 Results updated in run_125

📋 Are these results satisfactory? [Y/n/issues/more fields]: Y

📂 Project management:
  - Current project: Personal Shopping (5 runs)
  - Save this run to current project? [Y/n/change project]: change project

📋 Choose project:
  1. Personal Shopping (current, 5 runs)
  2. Home Goods Research (2 runs)
  3. Create new project

Select project [1-3]: 2

ℹ️ Run added to "Home Goods Research" project.
💡 Tip: Use 'brain export run_125 --format json' to export these results
```

## 4. Anti-Bot Protection Flow

```
$ brain scrape "Get sneaker prices from footlocker.com/product/nike-air-max-90"

🧠 Analyzing request with intent_inference...

ℹ️ Intent analysis complete:
  - Target URL: https://footlocker.com/product/nike-air-max-90
  - Fields to extract: price
  - Technical requirements: JavaScript rendering required (detected e-commerce site)

📋 Confirm extraction fields:
  > ◉ price
    ◯ title
    ◯ sizes
    ◯ colors
    ◯ availability

Do you want to proceed with these fields? [Y/n/edit]: edit

📋 Select fields to extract:
  > ◉ price
    ◉ title
    ◉ sizes
    ◉ colors
    ◯ availability

Is this selection correct? [Y/n]: Y

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  1. Browser: Playwright (Reason: JavaScript rendering needed)
  2. Parser: BeautifulSoup4 (Reason: HTML extraction for selected fields)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...  [######----------] 30%
📊 Loading page with Playwright...

❌ Error: Detected anti-bot protection (CAPTCHA/CloudFlare challenge)
This site is using bot protection that's blocking our standard scraper.

💡 Diagnostic from evaluator:
  - Error type: Anti-bot detection
  - Common causes: Cloudflare protection, Anti-scraping measures, Bot fingerprinting
  - Knowledge base entries: 5 similar issues found for footlocker.com

💡 Available actions:
  1. retry - Retry with anti-bot measures
  2. proxy - Use a proxy service
  3. stealth - Use stealth browser mode
  4. abort - Cancel this scrape

Choose an action [1-4]: 3

⚙️ Rebuilding pipeline with stealth mode...
🔄 [########------] 40% Switching browser engine
🔄 [############--] 60% Configuring stealth parameters
🔄 [################] 80% Optimizing request headers
🔄 [####################] 100% Finalizing updated pipeline

ℹ️ Updated pipeline:
  1. Browser: undetected-chromedriver (Reason: Stealth mode to bypass anti-bot)
  2. Parser: BeautifulSoup4 (Reason: HTML extraction for selected fields)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with stealth mode...  [####################] 100%

✅ Scraping complete! Found 4 fields:
  - Price: $120.00
  - Title: Nike Air Max 90 - Men's
  - Sizes: [7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 12, 13]
  - Colors: ["White/Black", "Black/White", "Grey/Blue", "Red/White"]

💾 Results saved as run_126

📋 Are these results satisfactory? [Y/n/issues/more fields]: issues

📋 What issues do you see with the results?
> The sizes are coming through as numbers, but I need them as strings with "US " prefix

ℹ️ Analyzing issue with evaluator...
🔄 [########------] 40% Examining extracted data
🔄 [################] 80% Generating transformation rules
🔄 [####################] 100% Creating data mapping

📋 Proposed fix:
  - Post-processing rule: Transform each size value to add "US " prefix
  - Example: 7 → "US 7"

Would you like to apply this transformation? [Y/n]: Y

🔄 Applying data transformation...  [####################] 100%

✅ Updated results:
  - Price: $120.00
  - Title: Nike Air Max 90 - Men's
  - Sizes: ["US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 10.5", "US 11", "US 12", "US 13"]
  - Colors: ["White/Black", "Black/White", "Grey/Blue", "Red/White"]

💾 Results updated in run_126

📋 Are these results satisfactory now? [Y/n/issues/more fields]: Y

📂 Project management:
  - Current project: Home Goods Research (3 runs)
  - Save this run to current project? [Y/n/change project]: change project

📋 Choose project:
  1. Personal Shopping (5 runs)
  2. Home Goods Research (current, 3 runs)
  3. Create new project

Select project [1-3]: 3

📋 Enter new project name: Sneaker Research

ℹ️ Created project "Sneaker Research" and added run_126 to it.
ℹ️ Note: For this site, future scrapes will automatically use stealth mode.
```

## 5. Multi-Page Scraping Flow

```
$ brain scrape "Get all laptop listings from the first 3 pages of bestbuy.com/laptops"

🧠 Analyzing request with intent_inference...

ℹ️ Intent analysis complete:
  - Target URL: https://bestbuy.com/laptops
  - Fields to extract: unspecified laptop listings
  - Technical requirements: 
    * JavaScript rendering required
    * Pagination handling needed (first 3 pages)

📋 For product listings, these fields are recommended:
  > ◉ title
    ◉ price
    ◉ rating
    ◯ model
    ◯ brand
    ◯ specifications
    ◯ url

Do you want to proceed with these fields? [Y/n/edit]: Y

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining pagination pattern
🔄 [################] 80% Configuring multi-page parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  1. Browser: Playwright (Reason: JavaScript rendering needed)
  2. Crawler: Custom BestBuy pagination handler (Reason: Multi-page extraction)
  3. Parser: BeautifulSoup4 (Reason: HTML extraction for product listings)

Does this pipeline look correct? [Y/n]: Y

📋 Configure pagination:
  - Pages to scrape: 3
  - Delay between pages: 2 seconds (recommended)

Are these settings correct? [Y/n/edit]: Y

🔄 Executing multi-page scrape with executor...  [######----------] 30%
📊 Page 1/3: Found 24 products...

🔄 Executing multi-page scrape with executor...  [############----] 60%
📊 Page 2/3: Found 24 products...

🔄 Executing multi-page scrape with executor...  [####################] 100%
📊 Page 3/3: Found 24 products...

✅ Scraping complete! Found 72 laptop listings across 3 pages.

📊 Sample of results (showing 3 of 72):
  1. HP - 15.6" Laptop - Intel Core i5 - 8GB RAM - 256GB SSD - $499.99 (★★★★☆)
  2. Dell - Inspiron 15.6" FHD Touch Laptop - i7 - 12GB - 512GB - $699.99 (★★★★★)
  3. ASUS - ROG Zephyrus 14" Gaming Laptop - Ryzen 9 - 16GB - RTX 3060 - $1,299.99 (★★★★☆)

💾 Results saved as run_127

📋 Are these results satisfactory? [Y/n/issues/more fields]: issues

📋 What issues do you see with the results?
> The RAM and storage are part of the title, I'd like them as separate fields

ℹ️ Analyzing issue with evaluator...
🔄 [########------] 40% Examining title patterns
🔄 [############--] 60% Identifying data patterns
🔄 [################] 80% Creating extraction rules
🔄 [####################] 100% Generating field mappings

📋 Proposed fix:
  - Add field extraction rules to parse RAM and storage from title
  - Create new fields: "ram" and "storage"
  - Example: "HP - 15.6" Laptop - Intel Core i5 - 8GB RAM - 256GB SSD" 
    → ram: "8GB", storage: "256GB SSD"

Would you like to apply this transformation? [Y/n]: Y

⚙️ Rebuilding pipeline with additional field extraction...
🔄 [########------] 40% Adding extraction rules
🔄 [################] 80% Reconfiguring parser
🔄 [####################] 100% Finalizing updated pipeline

🔄 Reprocessing data with new fields...  [####################] 100%

✅ Updated results with new fields:
  1. HP - 15.6" Laptop - Intel Core i5 - 8GB RAM - 256GB SSD
     - Price: $499.99
     - Rating: ★★★★☆
     - RAM: 8GB
     - Storage: 256GB SSD
  
  2. Dell - Inspiron 15.6" FHD Touch Laptop - i7 - 12GB - 512GB
     - Price: $699.99
     - Rating: ★★★★★
     - RAM: 12GB
     - Storage: 512GB
  
  3. ASUS - ROG Zephyrus 14" Gaming Laptop - Ryzen 9 - 16GB - RTX 3060
     - Price: $1,299.99
     - Rating: ★★★★☆
     - RAM: 16GB
     - Storage: Not specified

💾 Results updated in run_127

📋 Are these results satisfactory now? [Y/n/issues/more fields]: Y

📂 Project management:
  - Current project: Sneaker Research (1 run)
  - Save this run to current project? [Y/n/change project]: change project

📋 Choose project:
  1. Personal Shopping (5 runs)
  2. Home Goods Research (3 runs)
  3. Sneaker Research (current, 1 run)
  4. Create new project

Select project [1-4]: 4

📋 Enter new project name: Laptop Research

ℹ️ Created project "Laptop Research" and added run_127 to it.

📋 Would you like to:
  1. View more results
  2. Export results to file
  3. Filter results
  4. End session

Choose an option [1-4]: 2

📋 Export format:
  1. CSV
  2. JSON
  3. Excel

Choose a format [1-3]: 1

💾 Exporting to CSV...
✅ Exported to laptops_bestbuy_run127.csv in current directory

ℹ️ Run completed successfully.
```

## 6. Structured Command Flow

```
$ brain scrape --url https://amazon.ca/dp/B08WRBGSL2 --extract price,title,rating,reviews

ℹ️ Structured command detected:
  - Target URL: https://amazon.ca/dp/B08WRBGSL2
  - Fields to extract: price, title, rating, reviews
  - Technical requirements: Auto-detected from domain (JavaScript rendering required)

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  1. Browser: Playwright (Reason: JavaScript rendering needed for Amazon)
  2. Parser: BeautifulSoup4 (Reason: HTML extraction for specified fields)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...  [####################] 100%

✅ Scraping complete! Found 4 fields:
  - Price: $499.99
  - Title: Sony PlayStation 5 Console
  - Rating: 4.8/5
  - Reviews: [
      "Great console, fast shipping!",
      "Setup was easy, games look amazing",
      "Worth the wait, a true next-gen experience",
      ...and 47 more (use 'brain results run_128 --show-all' to view all)
    ]

💾 Results saved as run_128

📋 Are these results satisfactory? [Y/n/issues/more fields]: Y

📂 Project management:
  - Current project: Laptop Research (1 run)
  - Save this run to current project? [Y/n/change project]: change project

📋 Choose project:
  1. Personal Shopping (5 runs)
  2. Home Goods Research (3 runs)
  3. Sneaker Research (1 run)
  4. Laptop Research (current, 1 run)
  5. Create new project

Select project [1-5]: 1

ℹ️ Run added to "Personal Shopping" project.
ℹ️ Run completed successfully.
```

## 7. Project Organization Flow

```
$ brain projects

📂 Your projects:
┌─────────────────────┬──────────┬───────────────┬────────────────┐
│ Project Name        │ # of Runs│ Last Modified │ Tags           │
├─────────────────────┼──────────┼───────────────┼────────────────┤
│ Personal Shopping   │ 6        │ 2 minutes ago │ amazon, ebay   │
│ Home Goods Research │ 3        │ 25 minutes ago│ walmart        │
│ Sneaker Research    │ 1        │ 45 minutes ago│ footlocker     │
│ Laptop Research     │ 1        │ 15 minutes ago│ bestbuy        │
└─────────────────────┴──────────┴───────────────┴────────────────┘

📋 Project actions:
  1. View project details
  2. Create new project
  3. Edit project
  4. Delete project
  5. Export project
  6. Main menu

Choose an action [1-6]: 1

📋 Select project to view:
  1. Personal Shopping
  2. Home Goods Research
  3. Sneaker Research
  4. Laptop Research

Select project [1-4]: 1

📂 Project: Personal Shopping
  - Created: 2 days ago
  - 6 runs total
  - Tags: amazon, ebay
  - Last activity: 2 minutes ago

📊 Recent runs:
  1. run_128: Amazon PS5 (price, title, rating, reviews) - 2 minutes ago
  2. run_124: eBay item price - 50 minutes ago
  3. run_123: Amazon PS5 (price, title) - 1 hour ago
  4. run_122: Amazon headphones - 2 days ago
  ...and 2 more

📋 Project actions:
  1. View run details
  2. Add tag
  3. Export all runs
  4. Back to projects

Choose an action [1-4]: 1. View run details


```

## 8. Output Quality Improvement Flow

```
$ brain scrape "Get details for Airbnb listing https://airbnb.com/rooms/12345678"

🧠 Analyzing request with intent_inference...

ℹ️ Intent analysis complete:
  - Target URL: https://airbnb.com/rooms/12345678
  - Fields to extract: unspecified listing details
  - Technical requirements: JavaScript rendering required (detected Airbnb domain)

📋 For Airbnb listings, these fields are recommended:
  > ◉ title
    ◉ price
    ◉ rating
    ◉ location
    ◉ amenities
    ◯ host_info
    ◯ availability
    ◯ reviews

Do you want to proceed with these fields? [Y/n/edit]: Y

⚙️ Building scraping pipeline with pipeline_builder...
🔄 [####----------] 20% Analyzing page requirements
🔄 [########------] 40% Selecting appropriate tools
🔄 [############--] 60% Determining tool compatibility
🔄 [################] 80% Configuring tool parameters
🔄 [####################] 100% Finalizing pipeline

ℹ️ Proposed pipeline:
  1. Browser: Playwright (Reason: JavaScript rendering needed)
  2. Waiter: Dynamic content loader (Reason: Airbnb uses lazy loading)
  3. Parser: BeautifulSoup4 (Reason: HTML extraction for listing details)

Does this pipeline look correct? [Y/n]: Y

🔄 Executing scrape with executor...  [####################] 100%

✅ Scraping complete! Found 5 fields:
  - Title: Cozy Mountain Cabin with Stunning Views
  - Price: $159 per night
  - Rating: 4.92 (125 reviews)
  - Location: <div class="location-info">Asheville, North Carolina, United States</div>
  - Amenities: ["Wifi", "Kitchen", "Free parking", "Air conditioning", "<span class='amenity'>Hot tub</span>", "Heating"]

💾 Results saved as run_129

📋 Are these results satisfactory? [Y/n/issues/more fields]: issues

📋 What issues do you see with the results?
> The location still has HTML tags and the amenities have some HTML tags too

ℹ️ Analyzing issues with evaluator...
🔄 [########------] 40% Detecting HTML artifacts
🔄 [############--] 60% Creating cleaning rules
🔄 [################] 80% Generating transformations
🔄 [####################] 100% Validating clean output

📋 Proposed fixes:
  1. Strip HTML tags from location field
  2. Remove HTML tags from amenities list items

Would you like to apply these transformations? [Y/n]: Y

🔄 Applying data cleaning...  [####################] 100%

✅ Updated results with clean data:
  - Title: Cozy Mountain Cabin with Stunning Views
  - Price: $159 per night
  - Rating: 4.92 (125 reviews)
  - Location: Asheville, North Carolina, United States
  - Amenities: ["Wifi", "Kitchen", "Free parking", "Air conditioning", "Hot tub", "Heating"]

💾 Results updated in run_129

📋 Are these results satisfactory now? [Y/n/issues/more fields]: more fields

📋 Select additional fields to extract:
  > ◯ title (already extracted)
    ◯ price (already extracted)
    ◯ rating (already extracted)
    ◯ location (already extracted)
    ◯ amenities (already extracted)
    ◉ host_info
    ◉ availability
    ◯ reviews

Is this selection correct? [Y/n]: Y

⚙️ Updating pipeline for additional fields...
🔄 [########------] 40% Adding extraction parameters
🔄 [################] 80% Reconfiguring parser settings
🔄 [####################] 100% Finalizing updated pipeline

🔄 Extracting additional fields...  [####################] 100%

✅ Updated results with new fields:
  - Title: Cozy Mountain Cabin with Stunning Views
  - Price: $159 per night
  - Rating: 4.92 (125 reviews)
  - Location: Asheville, North Carolina, United States
  - Amenities: ["Wifi", "Kitchen", "Free parking", "Air conditioning", "Hot tub", "Heating"]
  - Host_info: {
      "name": "Sarah",
      "joined": "2018",
      "response_rate": "98%",
      "superhost": true
    }
  - Availability: {
      "min_stay": "2 nights",
      "next_available": "July 15-20",
      "calendar_updated": "2 days ago"
    }

💾 Results updated in run_129

📋 Are these results satisfactory now? [Y/n/issues/more fields]: Y

📂 Project management:
  - Current project: Personal Shopping (6 runs)
  - Save this run to current project? [Y/n/change project]: change project

📋 Choose project:
  1. Personal Shopping (current, 6 runs)
  2. Home Goods Research (3 runs)
  3. Sneaker Research (1 run)
  4. Laptop Research (1 run)
  5. Create new project

Select project [1-5]: 5

📋 Enter new project name: Travel Research

ℹ️ Created project "Travel Research" and added run_129 to it.

💡 The system has learned to clean HTML tags from Airbnb results for future scrapes.
💡 Tip: Use 'brain export run_129 --format json' to export these results
```



---



## [To Do Later Stage] Phase 2 for multiple runs and data aggregation 

## 9. Pipeline Management and Orchestration Flow

```
$ brain pipelines list --project "Travel Research"

📂 Project: Travel Research (2 runs, 2 pipelines)

⚙️ Available Pipelines:
┌─────────┬─────────────────────────────────────┬─────────────┬─────────────────┐
│ ID      │ Description                         │ Last Used   │ Success Rate    │
├─────────┼─────────────────────────────────────┼─────────────┼─────────────────┤
│ pipe_24 │ Airbnb Basic (Playwright + BS4)     │ 4 hours ago │ 100% (1/1 runs) │
│ pipe_31 │ Airbnb Full (Playwright + BS4 + JS) │ 1 hour ago  │ 100% (1/1 runs) │
└─────────┴─────────────────────────────────────┴─────────────┴─────────────────┘

📋 Pipeline actions:
  1. View pipeline details
  2. Clone and modify pipeline
  3. Create new pipeline
  4. Create multi-pipeline run
  5. Export pipeline configuration
  6. Main menu

Choose an action [1-6]: 4

📋 Create Multi-Pipeline Run (Orchestration)

ℹ️ A multi-pipeline run allows you to execute multiple pipelines and aggregate their results.

📋 Select pipelines to include:
  > ◉ pipe_24: Airbnb Basic
    ◉ pipe_31: Airbnb Full
    ◯ Create new pipeline

Is this selection correct? [Y/n]: Y

📋 Execution mode:
  1. Parallel (run all pipelines simultaneously)
  2. Sequential (run pipelines in order)
  3. Conditional (run subsequent pipelines based on results)

Select mode [1-3]: 1

📋 Target configuration:
  1. Same target for all pipelines
  2. Different targets for each pipeline

Select option [1-2]: 1

📝 Enter target URL: https://airbnb.com/rooms/9876543

📋 Result aggregation strategy:
  1. Merge all fields (overwrite duplicates with latest)
  2. Keep separate results by pipeline
  3. Custom aggregation rules

Select strategy [1-3]: 3

📋 Custom aggregation rules:
  - For duplicate fields, select source pipeline:
    * Title: [pipe_24/pipe_31]: pipe_24
    * Price: [pipe_24/pipe_31]: pipe_31
    * Rating: [pipe_24/pipe_31]: pipe_31
    * Location: [pipe_24/pipe_31]: pipe_24
    * Amenities: [pipe_24/pipe_31]: pipe_31
    * Host_info: [pipe_31 only]
    * Availability: [pipe_31 only]

Are these rules correct? [Y/n]: Y

ℹ️ Creating orchestration...

✅ Orchestration created:
  - ID: orch_12
  - Pipelines: pipe_24, pipe_31 (parallel execution)
  - Target: https://airbnb.com/rooms/9876543
  - Custom aggregation rules applied

📋 Would you like to:
  1. Execute this orchestration now
  2. Schedule for later
  3. Save as template
  4. Exit without running

Choose an action [1-4]: 1

🔄 Executing orchestration orch_12...

🔄 Starting parallel pipelines...
  
┌────────────────┬────────────┬────────────────┐
│ Pipeline       │ Status     │ Progress       │
├────────────────┼────────────┼────────────────┤
│ pipe_24 (Basic)│ Running    │ [#####-----] 25%│
│ pipe_31 (Full) │ Running    │ [####------] 20%│
└────────────────┴────────────┴────────────────┘

🔄 Updating status...
  
┌────────────────┬────────────┬────────────────┐
│ Pipeline       │ Status     │ Progress       │
├────────────────┼────────────┼────────────────┤
│ pipe_24 (Basic)│ Running    │ [########--] 80%│
│ pipe_31 (Full) │ Running    │ [######----] 60%│
└────────────────┴────────────┴────────────────┘

🔄 Updating status...
  
┌────────────────┬────────────┬────────────────────┐
│ Pipeline       │ Status     │ Progress           │
├────────────────┼────────────┼────────────────────┤
│ pipe_24 (Basic)│ Completed  │ [##########] 100%  │
│ pipe_31 (Full) │ Running    │ [########--] 80%   │
└────────────────┴────────────┴────────────────────┘

🔄 Updating status...
  
┌────────────────┬────────────┬────────────────────┐
│ Pipeline       │ Status     │ Progress           │
├────────────────┼────────────┼────────────────────┤
│ pipe_24 (Basic)│ Completed  │ [##########] 100%  │
│ pipe_31 (Full) │ Completed  │ [##########] 100%  │
└────────────────┴────────────┴────────────────────┘

🔄 Aggregating results based on custom rules...

✅ Orchestration completed! Aggregated results:
  - Title: Mountain Retreat with Lake Access (from pipe_24)
  - Price: $189 per night (from pipe_31)
  - Rating: 4.85 (97 reviews) (from pipe_31)
  - Location: Boulder, Colorado, United States (from pipe_24)
  - Amenities: ["Wifi", "Kitchen", "Fireplace", "Washer/Dryer", "Lake access", "Hiking trails"] (from pipe_31)
  - Host_info: {
      "name": "Michael",
      "joined": "2016",
      "response_rate": "100%",
      "superhost": true
    } (from pipe_31)
  - Availability: {
      "min_stay": "3 nights",
      "next_available": "August 5-12",
      "calendar_updated": "1 day ago"
    } (from pipe_31)

💾 Results saved as orchestration orch_12 (individual runs: run_130, run_131)

📋 Are these aggregated results satisfactory? [Y/n/issues]: Y

📂 Project management:
  - Current project: Travel Research (3 runs, 2 pipelines, 1 orchestration)
  - Orchestration automatically added to current project

ℹ️ Orchestration completed successfully.
💡 Tip: Use 'brain orchestrations list' to view all your multi-pipeline runs
```

Now let's create another example showing a sequential orchestration with conditional logic:

```
$ brain orchestrations create

📋 Create New Orchestration

ℹ️ Available projects:
  1. Personal Shopping (6 runs)
  2. Home Goods Research (3 runs)
  3. Sneaker Research (1 run)
  4. Laptop Research (1 run)
  5. Travel Research (3 runs, 2 pipelines, 1 orchestration)

Select project [1-5]: 1

📂 Project: Personal Shopping (6 runs, 3 pipelines)

⚙️ Available Pipelines:
┌─────────┬───────────────────────────────────┬─────────────┬─────────────────┐
│ ID      │ Description                       │ Last Used   │ Success Rate    │
├─────────┼───────────────────────────────────┼─────────────┼─────────────────┤
│ pipe_01 │ Amazon Basic (Playwright + BS4)   │ 1 day ago   │ 100% (4/4 runs) │
│ pipe_08 │ eBay Basic (Playwright + BS4)     │ 2 days ago  │ 50% (1/2 runs)  │
│ pipe_15 │ Amazon Full (Playwright + Scrapy) │ 5 hours ago │ 100% (1/1 runs) │
└─────────┴───────────────────────────────────┴─────────────┴─────────────────┘

📋 Select pipelines to include:
  > ◉ pipe_01: Amazon Basic
    ◉ pipe_15: Amazon Full
    ◯ pipe_08: eBay Basic
    ◯ Create new pipeline

Is this selection correct? [Y/n]: Y

📋 Execution mode:
  1. Parallel (run all pipelines simultaneously)
  2. Sequential (run pipelines in order)
  3. Conditional (run subsequent pipelines based on results)

Select mode [1-3]: 3

📋 Configure conditional execution:
  - First pipeline to run: pipe_01 (Amazon Basic)
  
  - If pipe_01 succeeds AND finds price below $300:
    Run next pipeline: pipe_15 (Amazon Full)
  
  - If pipe_01 fails OR price is $300 or above:
    Skip remaining pipelines

Is this configuration correct? [Y/n]: Y

📝 Enter target URL: https://amazon.com/dp/B09V3JN8P9

📋 Result aggregation strategy:
  1. Merge all fields (overwrite duplicates with latest)
  2. Keep separate results by pipeline
  3. Custom aggregation rules

Select strategy [1-3]: 1

ℹ️ Creating orchestration...

✅ Orchestration created:
  - ID: orch_13
  - Pipelines: pipe_01 → pipe_15 (conditional execution)
  - Target: https://amazon.com/dp/B09V3JN8P9
  - Merge aggregation strategy

📋 Would you like to:
  1. Execute this orchestration now
  2. Schedule for later
  3. Save as template
  4. Exit without running

Choose an action [1-4]: 1

🔄 Executing orchestration orch_13...

🔄 Running pipeline pipe_01 (Amazon Basic)...  [##########] 100%

ℹ️ Checking condition: Price below $300?
  - Extracted price: $249.99
  - Condition result: TRUE ✓

🔄 Condition met, running pipeline pipe_15 (Amazon Full)...  [##########] 100%

🔄 Aggregating results using merge strategy...

✅ Orchestration completed! Aggregated results:
  - Title: Smartphone XYZ Pro (128GB, Midnight Black)
  - Price: $249.99
  - Rating: 4.6/5
  - Reviews: 1,234 ratings
  - Availability: In Stock
  - Features: [
      "6.1-inch Super Retina XDR display",
      "Cinematic mode in 1080p at 30 fps",
      "A15 Bionic chip",
      "5G capable",
      "128GB storage"
    ]
  - Seller: Amazon.com
  - Shipping: Free with Prime

💾 Results saved as orchestration orch_13 (individual runs: run_132, run_133)

📋 Are these aggregated results satisfactory? [Y/n/issues]: Y

📂 Project management:
  - Current project: Personal Shopping (8 runs, 3 pipelines, 1 orchestration)
  - Orchestration automatically added to current project

ℹ️ Orchestration completed successfully.
```

And finally, let's create an example showing pipeline creation and management:

```
$ brain pipelines create

📋 Create New Pipeline

ℹ️ Available projects:
  1. Personal Shopping (8 runs, 3 pipelines, 1 orchestration)
  2. Home Goods Research (3 runs)
  3. Sneaker Research (1 run)
  4. Laptop Research (1 run)
  5. Travel Research (3 runs, 2 pipelines, 1 orchestration)

Select project [1-5]: 3

📂 Project: Sneaker Research (1 run, 0 pipelines)

ℹ️ Pipeline configuration

📋 Select tools for this pipeline:
  1. Browser engines
  2. Parsers
  3. Interaction handlers
  4. Data processors
  5. Helper tools

Select category [1-5]: 1

📋 Select browser engine:
  > ◉ Playwright (Recommended for most sites)
    ◯ Selenium
    ◯ Undetected ChromeDriver (Good for anti-bot protection)
    ◯ RequestsHTML (Lightweight, limited JS support)

Is this selection correct? [Y/n]: Y

📋 Select category [1-5]: 2

📋 Select parser:
  > ◉ BeautifulSoup4 (Recommended for most extractions)
    ◯ Scrapy
    ◯ XPath
    ◯ Custom Regex

Is this selection correct? [Y/n]: Y

📋 Select category [1-5]: 3

📋 Select interaction handlers:
  > ◉ Auto-scroll (Loads lazy content)
    ◉ Click expanders (Opens collapsed sections)
    ◯ Form filler
    ◯ CAPTCHA handler

Is this selection correct? [Y/n]: Y

📋 Select category [1-5]: 4

📋 Select data processors:
  > ◉ HTML cleaner (Removes tags)
    ◉ Currency normalizer
    ◯ Date formatter
    ◯ Unit converter

Is this selection correct? [Y/n]: Y

📋 Select category [1-5]: 5

📋 Select helper tools:
  > ◉ Retry handler (Automatic retries on failure)
    ◉ Screenshot capture (For debugging)
    ◯ Header rotator
    ◯ Cookie manager

Is this selection correct? [Y/n]: Y

📋 Pipeline specific settings:
  - Browser viewport: 1920x1080
  - User agent: Default (Chrome)
  - Wait timeout: 30 seconds
  - Retry attempts: 3

Are these settings correct? [Y/n/edit]: Y

📝 Enter pipeline name: Sneaker Site Standard

📝 Enter pipeline description (optional): Standard configuration for sneaker sites with anti-bot protection

ℹ️ Creating pipeline...

✅ Pipeline created:
  - ID: pipe_32
  - Name: Sneaker Site Standard
  - Tools: Playwright, BeautifulSoup4, Auto-scroll, Click expanders, HTML cleaner, Currency normalizer, Retry handler, Screenshot capture
  - Project: Sneaker Research

📋 Would you like to:
  1. Test this pipeline now
  2. Use in a new orchestration
  3. Clone this pipeline
  4. Exit

Choose an action [1-4]: 1

📝 Enter test URL: https://footlocker.com/product/nike-air-force-1-07-mens/CW2288100.html

🔄 Testing pipeline pipe_32...

🔄 Executing browser engine...  [####------] 20%
📊 Launching browser...

🔄 Executing browser engine...  [########--] 40%
📊 Loading page...

🔄 Executing interaction handlers...  [############] 60%
📊 Auto-scrolling page...

🔄 Executing interaction handlers...  [################] 80%
📊 Clicking expanders...

🔄 Executing parser...  [####################] 100%
📊 Extracting data...

✅ Test completed! Sample of extracted data:
  - Title: Nike Air Force 1 '07 - Men's
  - Price: $110.00
  - Available sizes: ["US 7", "US 7.5", "US 8", "US 8.5", "US 9", "US 9.5", "US 10", "US 10.5", "US 11", "US 12", "US 13"]
  - Color: White/White
  - Brand: Nike
  - Style: CW2288100

💾 Test results saved as run_134 (test)

📋 Are these test results satisfactory? [Y/n/issues]: Y

ℹ️ Pipeline test completed successfully.
💡 You can now use this pipeline in regular scrapes or orchestrations
```

In these examples, I've demonstrated:

1. **Pipeline Listing and Management**: Users can view, create, and manage pipelines within projects

2. **Orchestration Creation**: Users can create orchestrations (multi-pipeline runs) with different execution modes:
   - Parallel execution (all pipelines run simultaneously)
   - Sequential execution (pipelines run in order)
   - Conditional execution (subsequent pipelines run based on results of earlier ones)

3. **Result Aggregation**: Users can specify how results from multiple pipelines should be combined:
   - Simple merging (latest wins for duplicates)
   - Keeping results separate by pipeline
   - Custom rules for each field

4. **Pipeline Creation**: Users can build custom pipelines by selecting tools from different categories:
   - Browser engines
   - Parsers
   - Interaction handlers
   - Data processors
   - Helper tools

5. **Pipeline Testing**: Users can test pipelines before using them in production

The key modules that would need to be developed to support this functionality:

1. **`pipeline_builder`**: Creates and configures pipelines of tools
2. **`orchestrator`**: Manages execution of multiple pipelines and aggregates results
3. **`project_manager`**: Organizes runs, pipelines, and orchestrations into projects
4. **`executor`**: Executes individual pipeline runs
5. **`scrape_analyzer`**: Analyzes results and provides diagnostics

This hierarchy allows for flexibility while maintaining organization:
- Projects contain related scraping activities
- Pipelines define tool configurations for specific scraping needs
- Runs are individual executions
- Orchestrations combine multiple pipelines for complex scraping tasks