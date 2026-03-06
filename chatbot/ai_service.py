"""AI Service - Handles Groq API and local farming knowledge"""

from groq import Groq
from django.conf import settings


SYSTEM_PROMPT = """You are Nhimbe AI, a knowledgeable and friendly agricultural advisor 
built specifically for Zimbabwean smallholder farmers.

Your expertise covers:
- Crops commonly grown in Zimbabwe: maize, tobacco, groundnuts, sorghum, millet, 
  cotton, soybeans, sunflower, wheat, vegetables (tomatoes, onions, cabbages, leafy greens)
- Livestock: cattle (including Brahman, Mashona, Tuli breeds), goats, chickens 
  (broilers and layers), pigs, rabbits
- Zimbabwean soil types and their management
- Local climate patterns, rainfall seasons (October-March wet season, April-September dry)
- Natural regions of Zimbabwe (Region I through V) and what grows best in each
- Pest and disease management relevant to Southern Africa
- Small-scale irrigation methods suitable for rural Zimbabwe
- Post-harvest handling and storage
- Basic agribusiness: pricing, markets like Mbare Musika, contract farming
- Government agricultural programs and extension services
- Conservation farming and climate-smart agriculture

Guidelines:
- Give practical, actionable advice that smallholder farmers can implement
- Consider limited resources and budgets in your recommendations
- Reference local conditions, seasons, and practices when relevant
- Use simple, clear language avoiding overly technical jargon
- When discussing chemicals or pesticides, mention safety precautions
- If you genuinely do not know something, say so honestly and suggest 
  consulting a local agricultural extension officer (AGRITEX)
- Respond in the same language the user writes in. If they write in English, 
  respond entirely in English. If they write in Shona, respond entirely in Shona.
  If they write in Ndebele, respond entirely in Ndebele. Do NOT mix languages.
- Be warm, encouraging, and supportive
- Keep responses focused and not too long unless the user asks for detail

You are NOT a medical doctor, veterinarian, or financial advisor. For serious 
animal health issues, recommend consulting a veterinarian. For financial decisions, 
recommend speaking with agricultural finance institutions.

IMPORTANT: Never mix languages in your response. Stick to one language throughout."""


LOCAL_KNOWLEDGE = {

    # ─────────────────────────────────────────────────────────────
    # ORIGINAL AGRONOMIC HOW-TO ENTRIES — unchanged
    # ─────────────────────────────────────────────────────────────

    'planting_maize': {
        'keywords': ['plant maize', 'grow maize', 'maize planting', 'when to plant maize', 'maize season'],
        'answer': (
            'In Zimbabwe, maize planting typically begins with the onset of rains, '
            'usually between mid-November and mid-December. Here are the key steps:\n\n'
            '1. Land preparation: Plough or dig your field before the rains start\n'
            '2. Spacing: Plant seeds 25-30cm apart in rows 75-90cm apart\n'
            '3. Depth: Plant seeds 5-7cm deep\n'
            '4. Fertiliser: Apply compound D (basal) at planting, then top-dress '
            'with Ammonium Nitrate (AN) at 4-6 weeks\n'
            '5. Varieties: Consider SC513, SC719, or PAN varieties depending on your region\n\n'
            'For Natural Region III-V, consider drought-tolerant varieties and conservation farming methods.'
        )
    },

    'tomato_growing': {
        'keywords': ['grow tomato', 'tomato farming', 'plant tomatoes', 'tomato disease'],
        'answer': (
            'Tomatoes grow well in most parts of Zimbabwe. Key tips:\n\n'
            '1. Start seedlings in a nursery bed, transplant after 4-6 weeks\n'
            '2. Spacing: 60cm between plants, 90cm between rows\n'
            '3. Water regularly but avoid wetting the leaves\n'
            '4. Stake or cage your plants for support\n'
            '5. Common diseases: Early blight, late blight, bacterial wilt\n'
            '6. Use copper-based fungicides preventively\n'
            '7. Best varieties for Zimbabwe: Rodade, Star 9003, Tengeru\n\n'
            'Tomatoes do well in Mazowe, Mutoko, and Honde Valley areas.'
        )
    },

    'chicken_broiler': {
        'keywords': ['broiler', 'chicken farming', 'raise chickens', 'poultry farming', 'broiler chicken'],
        'answer': (
            'Broiler chicken farming is popular in Zimbabwe. Here is a basic guide:\n\n'
            '1. Housing: 1 square foot per bird, good ventilation, clean bedding\n'
            '2. Chicks: Buy from reliable suppliers like Irvines or Suncrest\n'
            '3. Feed schedule:\n'
            '   - Week 1-3: Starter mash\n'
            '   - Week 3-5: Grower mash\n'
            '   - Week 5-8: Finisher mash\n'
            '4. Vaccinations: Newcastle disease, Gumboro at recommended ages\n'
            '5. Temperature: Start at 32-35 degrees C, reduce by 3 degrees each week\n'
            '6. Water: Always provide clean, fresh water\n'
            '7. Selling: Target 6-8 weeks for market weight (1.8-2.2kg)\n\n'
            'Budget for about 100 birds to start and reinvest profits.'
        )
    },

    'cattle_feeding': {
        'keywords': ['feed cattle', 'cattle feed', 'cow feeding', 'cattle nutrition', 'livestock feed'],
        'answer': (
            'Feeding cattle in Zimbabwe depends on the season:\n\n'
            'Wet season (October-March):\n'
            '- Natural grazing is usually sufficient\n'
            '- Supplement with salt licks and minerals\n\n'
            'Dry season (April-September):\n'
            '- Grazing quality drops, supplementation needed\n'
            '- Options: crop residues (maize stover), hay, silage\n'
            '- Supplement with protein: cotton seed cake, sunflower cake\n'
            '- Salt and mineral licks are essential year-round\n\n'
            'For Mashona and Tuli breeds, they are hardy and do well on natural veld. '
            'Cross-breeds with Brahman need more supplementation.\n\n'
            'Always ensure access to clean water. A mature cow drinks 40-60 litres daily.'
        )
    },

    'soil_testing': {
        'keywords': ['soil test', 'test soil', 'soil type', 'soil ph', 'soil fertility'],
        'answer': (
            'Soil testing is important for knowing what your soil needs:\n\n'
            '1. Where to test: Contact your nearest AGRITEX office or the '
            'Chemistry and Soil Research Institute in Harare\n'
            '2. How to collect samples:\n'
            '   - Take samples from 10-15 spots across your field\n'
            '   - Dig 15-20cm deep\n'
            '   - Mix all samples together in a clean bucket\n'
            '   - Take about 500g of the mixed sample to the lab\n'
            '3. What you learn: pH level, nitrogen, phosphorus, potassium levels\n'
            '4. Cost: Usually affordable, sometimes subsidised\n\n'
            'Most Zimbabwean soils are slightly acidic. If pH is below 5.5, '
            'consider applying agricultural lime before planting.'
        )
    },

    'conservation_farming': {
        'keywords': ['conservation farming', 'pfumvudza', 'climate smart', 'drought', 'dry spell'],
        'answer': (
            'Conservation farming (including the Pfumvudza/Intwasa programme) '
            'helps farmers grow more with less water:\n\n'
            '1. Minimum tillage: Use planting basins instead of ploughing the whole field\n'
            '2. Mulching: Cover soil with crop residues to retain moisture\n'
            '3. Crop rotation: Alternate maize with legumes like groundnuts or cowpeas\n'
            '4. Planting basins: Dig holes 15cm x 15cm x 15cm, spaced 60-90cm apart\n'
            '5. Micro-dosing fertiliser: Place fertiliser directly in the basin\n\n'
            'Benefits:\n'
            '- Uses 50-70% less water than conventional farming\n'
            '- Can be done without a plough or tractor\n'
            '- Government provides free inputs through Pfumvudza programme\n\n'
            'Contact your local AGRITEX officer to register for the programme.'
        )
    },

    'groundnuts': {
        'keywords': ['groundnut', 'peanut', 'grow groundnuts', 'groundnut farming'],
        'answer': (
            'Groundnuts are an excellent cash and food crop for Zimbabwe:\n\n'
            '1. Planting time: November to mid-December with the rains\n'
            '2. Varieties: Natal Common, Flamingo, Falcon for confectionery\n'
            '3. Spacing: 45cm between rows, 10-15cm between plants\n'
            '4. Seed rate: About 80-100kg per hectare\n'
            '5. Soil: Prefer well-drained sandy loam soils\n'
            '6. Fertiliser: Compound L at planting, groundnuts fix their own nitrogen\n'
            '7. Harvesting: 120-150 days after planting when leaves yellow\n'
            '8. Drying: Dry in windrows then on racks, avoid ground contact\n\n'
            'Groundnuts do well in Natural Regions II-IV. '
            'Good market demand for both raw nuts and peanut butter production.'
        )
    },

    'tobacco': {
        'keywords': ['tobacco', 'tobacco farming', 'grow tobacco', 'tobacco curing'],
        'answer': (
            'Tobacco is Zimbabwe\'s top export crop. Key steps:\n\n'
            '1. Seedbeds: Start in August-September under shade\n'
            '2. Transplanting: November-December when seedlings are 15cm tall\n'
            '3. Spacing: 120cm between rows, 50-60cm between plants\n'
            '4. Fertiliser: Heavy feeder, requires compound S and AN top-dressing\n'
            '5. Topping and suckering: Remove flower heads and suckers\n'
            '6. Harvesting: Reap leaves from bottom up as they ripen\n'
            '7. Curing: Flue-cured in barns at specific temperatures\n'
            '8. Grading and selling: Sell at auction floors in Harare\n\n'
            'Registration with TIMB (Tobacco Industry and Marketing Board) is required. '
            'Contract farming with companies like Mashonaland Tobacco Company '
            'provides inputs and guaranteed market.'
        )
    },

    # ─────────────────────────────────────────────────────────────
    # RECENT STATISTICS & CURRENT INFORMATION (2024/2025)
    # These bypass the skip_words filter so farmers always get
    # current Zimbabwe-specific data when asking about these topics.
    # ─────────────────────────────────────────────────────────────

    'maize_production_stats': {
        'keywords': [
            'maize production', 'maize yield', 'maize statistics', 'maize output',
            'maize harvest', 'how much maize', 'maize tonnes', 'maize shortage',
            'maize surplus', 'national maize', 'cereal production', 'grain production',
        ],
        'answer': (
            'Zimbabwe Maize Production — Recent Figures:\n\n'
            '2023/2024 season:\n'
            '- National production estimated at approximately 1.06 million metric tonnes\n'
            '- A major decline caused by El Nino drought — one of the worst seasons '
            'in recent memory for dryland farmers\n'
            '- Most affected provinces: Matabeleland North & South, Masvingo, '
            'southern Midlands\n'
            '- ZIMVAC estimated over 7.6 million people faced food insecurity by mid-2024\n'
            '- Government declared a State of Disaster in April 2024\n\n'
            '2022/2023 season (for comparison):\n'
            '- Production reached approximately 2.1 million metric tonnes — a good year\n\n'
            'Implications for farmers:\n'
            '- Grain prices rose sharply throughout 2024 due to the deficit\n'
            '- GMB imported maize to partially cover the shortage\n'
            '- For 2024/25: La Nina conditions forecast — expect better rains\n'
            '- Plant drought-tolerant varieties (SC403, SC647, ZM309) regardless\n'
            '- Register for Pfumvudza inputs early — August to October is the window'
        )
    },

    'tobacco_stats': {
        'keywords': [
            'tobacco production', 'tobacco statistics', 'tobacco yield', 'tobacco sales',
            'tobacco price', 'tobacco auction', 'tobacco export', 'tobacco revenue',
            'how much tobacco', 'tobacco kg', 'tobacco million', 'timb',
            'tobacco 2024', 'tobacco selling season',
        ],
        'answer': (
            'Zimbabwe Tobacco Industry — 2024 Figures:\n\n'
            '2024 selling season highlights:\n'
            '- Total tobacco sold: approximately 296 million kg\n'
            '- Up from 233 million kg in 2023 — highest volume in over two decades\n'
            '- Average price: approximately USD 3.40 per kg at auction\n'
            '- Total revenue: over USD 1 billion for the season\n'
            '- Zimbabwe is now Africa\'s largest tobacco producer and 4th globally '
            '(after China, Brazil, and India)\n\n'
            'Grower breakdown (2024):\n'
            '- Communal and A1 smallholder farmers contributed roughly 60% of volume\n'
            '- Majority sell through contract arrangements\n'
            '- Both Boka and ZTGH auction floors remain active in Harare\n\n'
            'How to participate:\n'
            '- All growers must register with TIMB before planting — free registration\n'
            '- TIMB offices: Harare, Marondera, Mvurwi, Karoi, Bindura\n'
            '- Contract companies providing inputs: Alliance One, Mashonaland Tobacco, '
            'Tribac, Zimbabwe Leaf Tobacco (ZLT)\n\n'
            '2024/25 target: Government is aiming for 300 million kg. '
            'Register with TIMB early as contract input allocations fill up quickly.'
        )
    },

    'fertiliser_prices': {
        'keywords': [
            'fertiliser price', 'fertiliser cost', 'compound d price', 'an price',
            'ammonium nitrate price', 'basal fertiliser', 'top dressing price',
            'how much fertiliser', 'fertiliser 2024', 'fertiliser usd',
            'fertiliser shortage', 'where to buy fertiliser', 'compound c price',
        ],
        'answer': (
            'Fertiliser Prices in Zimbabwe — 2024/25 Season (approximate):\n\n'
            'Compound D — basal dressing (50kg bag):\n'
            '- USD 28-35 depending on supplier and location\n\n'
            'Ammonium Nitrate (AN) — top dressing (50kg bag):\n'
            '- USD 25-32 per bag\n\n'
            'Compound C (50kg bag):\n'
            '- USD 30-36 per bag\n\n'
            'Where to buy:\n'
            '- Major brands: Windmill, Sable Chemical, Omnia, Agricura\n'
            '- Retailers: Farmers World, Farm & City Centre, AgriMart\n'
            '- GMB depots for subsidised government scheme allocations\n\n'
            'Free/subsidised fertiliser:\n'
            '- Pfumvudza/Intwasa: seed + fertiliser package for registered '
            'small-scale farmers. Contact your AGRITEX ward officer — bring your ID\n'
            '- Presidential Input Scheme: targets vulnerable households via village '
            'headman and ward councillor\n\n'
            'Buying tip: Purchase in September-October before the November rush. '
            'Prices typically rise 10-15% once planting season begins.'
        )
    },

    'grain_prices': {
        'keywords': [
            'grain price', 'maize price', 'sell maize', 'gmb price', 'maize market price',
            'how much maize sell', 'maize per tonne', 'sorghum price', 'wheat price',
            'groundnut price', 'commodity price', 'crop price 2024', 'soyabean price',
            'sunflower price', 'where to sell grain',
        ],
        'answer': (
            'Crop Producer Prices in Zimbabwe — 2024/25 (approximate):\n\n'
            'GMB (Grain Marketing Board) official prices:\n'
            '- Maize:      USD 390 per tonne  (~USD 19.50 per 50kg bag)\n'
            '- Wheat:      USD 510 per tonne\n'
            '- Sorghum:    USD 390 per tonne\n'
            '- Soyabeans:  USD 600 per tonne\n'
            '- Sunflower:  USD 550 per tonne\n\n'
            'Open market prices (vary by season and location):\n'
            '- Maize grain:   USD 280-450 per tonne (higher in drought years)\n'
            '- Groundnuts:    USD 800-1,200 per tonne (confectionery grade)\n\n'
            'Note: In the 2024 drought year, open market prices exceeded GMB prices '
            'significantly. In a good 2024/25 season, open market may be lower.\n\n'
            'Where to sell:\n'
            '- GMB depots (guaranteed price, nationwide, can be slow to pay)\n'
            '- Private grain traders (faster payment, negotiate your price)\n'
            '- Mbare Musika, Harare (vegetables and small quantities)\n'
            '- Contract companies (fixed price agreed before planting)\n\n'
            'Tip: Store grain safely for 2-3 months after harvest and sell when '
            'prices are higher, typically June-September.'
        )
    },

    'el_nino_drought_2024': {
        'keywords': [
            'el nino', 'drought 2024', 'rainfall 2024', 'poor rains', 'low rainfall',
            'failed rains', 'climate 2024', 'weather 2024', 'drought effect',
            'food shortage', 'hunger 2024', 'food crisis', 'zimvac',
            'state of disaster', 'food insecurity',
        ],
        'answer': (
            'El Nino Drought — Impact on Zimbabwe 2023/24:\n\n'
            'What happened:\n'
            '- The 2023/24 season was severely hit by El Nino-induced dry conditions\n'
            '- Rainfall was 40-60% below normal across southern and central provinces\n'
            '- Worst affected: Matabeleland North, Matabeleland South, Masvingo, '
            'southern Midlands\n'
            '- Manicaland and northern Mashonaland received comparatively better rains\n\n'
            'Impact on food security:\n'
            '- Maize production fell to ~1.06 million tonnes (vs 2.1M in 2022/23)\n'
            '- ZIMVAC reported over 7.6 million people food insecure by mid-2024\n'
            '- President Mnangagwa declared a National State of Disaster in April 2024\n'
            '- WFP, UNICEF, and NGOs scaled up emergency food assistance\n'
            '- Cattle deaths reported in drier regions due to pasture failure\n\n'
            'Looking ahead to 2024/25:\n'
            '- La Nina conditions developing — forecasters expect above-normal rainfall\n'
            '- MSD Zimbabwe seasonal forecast: generally favourable for most regions\n'
            '- Still plant drought-tolerant varieties (SC403, ZM309) as backup\n'
            '- Register for Pfumvudza/government inputs before October cutoff\n'
            '- Consider water harvesting if you have the means'
        )
    },

    'rainfall_forecast_2025': {
        'keywords': [
            'rainfall forecast', 'rain forecast', 'weather forecast', 'rains 2025',
            'when will it rain', 'rainy season', 'seasonal forecast', 'msd forecast',
            'good rains', 'la nina', 'rainfall prediction', 'planting forecast',
            'start of rains', 'onset of rains',
        ],
        'answer': (
            'Zimbabwe Rainfall Forecast — 2024/25 Season:\n\n'
            'Overall outlook:\n'
            '- La Nina conditions are developing after the 2023/24 El Nino year\n'
            '- La Nina typically brings above-normal to normal rainfall to Zimbabwe\n'
            '- MSD Zimbabwe is forecasting a generally favourable season for 2024/25\n\n'
            'Expected onset of rains by province:\n'
            '- Mashonaland provinces: mid-October to early November 2024\n'
            '- Midlands and Masvingo: mid-November 2024\n'
            '- Matabeleland provinces: late November to December 2024\n\n'
            'What farmers should do now:\n'
            '1. Prepare land early — plough before rains arrive, not after\n'
            '2. Secure seed and fertiliser in September-October (before price rises)\n'
            '3. Register for Pfumvudza inputs at your AGRITEX ward office immediately\n'
            '4. If you have irrigation, plant winter wheat or vegetables now\n'
            '5. Even in a good forecast year, plant drought-tolerant varieties as backup\n\n'
            'Stay updated via:\n'
            '- MSD Zimbabwe bulletins on ZBC Radio (daily weather + seasonal advisories)\n'
            '- AGRITEX seasonal advisory meetings at district offices\n'
            '- SADC Climate Services Centre quarterly outlook forums'
        )
    },

    'government_input_schemes': {
        'keywords': [
            'government inputs', 'free inputs', 'government seed', 'input scheme',
            'pfumvudza inputs', 'presidential inputs', 'government programme',
            'free seed', 'subsidised inputs', 'agritex register', 'how to register',
            'input support', 'government support farmers', 'command agriculture',
            'government farming help',
        ],
        'answer': (
            'Government Agricultural Input Schemes — Zimbabwe 2024/25:\n\n'
            '1. Pfumvudza / Intwasa Programme:\n'
            '   - For communal and A1 small-scale farmers\n'
            '   - Package: certified seed + Compound D + AN fertiliser\n'
            '   - Farmer commits to conservation farming (planting basins, mulching)\n'
            '   - Register with your AGRITEX ward extension officer\n'
            '   - Registration window: August to October — do not miss this\n'
            '   - Bring: National ID and proof of land (letter from headman is enough)\n\n'
            '2. Presidential Input Scheme:\n'
            '   - Targets the most vulnerable and food-insecure households\n'
            '   - Selected at village and ward level through local leadership\n'
            '   - Speak to your village headman or ward councillor\n\n'
            '3. Command Agriculture:\n'
            '   - Mainly A2 and larger commercial farmers\n'
            '   - Inputs on credit, repaid from harvest proceeds\n'
            '   - Apply through Agribank or the Ministry of Agriculture\n\n'
            '4. Tobacco Contract Farming:\n'
            '   - Seed, chemicals, curing fuel on credit from the contractor\n'
            '   - Repaid at point of sale from tobacco proceeds\n'
            '   - Companies: Alliance One, Mashonaland Tobacco, Tribac, ZLT\n\n'
            'Key reminder: All schemes fill quickly. Register in August-September.'
        )
    },

    'livestock_prices_2024': {
        'keywords': [
            'cattle price', 'sell cattle', 'cow price', 'bull price', 'livestock price',
            'goat price', 'pig price', 'chicken price', 'broiler price', 'egg price',
            'how much cow', 'how much chicken', 'livestock market 2024',
            'day old chick price', 'doc price', 'layer price',
        ],
        'answer': (
            'Livestock Market Prices — Zimbabwe 2024 (approximate):\n\n'
            'Cattle:\n'
            '- Mature grade A bull (good condition): USD 600-900\n'
            '- Breeding cow: USD 500-750\n'
            '- Weaner calf: USD 200-350\n'
            '- Note: Cattle prices rose in 2024 due to drought-driven destocking\n'
            '- Best prices at CSC (Cold Storage Company) auctions\n\n'
            'Goats:\n'
            '- Mature goat: USD 30-60 (size and condition dependent)\n'
            '- High demand during festive season (November-January)\n\n'
            'Pigs:\n'
            '- Mature pig at 80-90kg: USD 120-180\n'
            '- Weaned piglets: USD 20-35 each\n\n'
            'Broiler chickens (live weight):\n'
            '- 1.8-2.0kg bird: USD 5-7\n'
            '- Dressed and packaged: USD 7-10 per bird\n\n'
            'Eggs:\n'
            '- Tray of 30 eggs: USD 4.50-6.00\n\n'
            'Day-old chicks (DOC):\n'
            '- Broiler DOC: USD 1.20-1.80 each (Irvines, Suncrest)\n'
            '- Layer DOC: USD 1.50-2.00 each\n\n'
            'Where to sell: CSC auctions, private abattoirs, Mbare Musika, '
            'local butchers, direct to households and restaurants.'
        )
    },

    'agribank_loans': {
        'keywords': [
            'agribank', 'farming loan', 'agricultural loan', 'farm loan',
            'borrow money farming', 'credit farming', 'finance farming',
            'agricultural finance', 'loan for farming', 'how to get loan',
            'cbz agro', 'farming credit', 'smedco',
        ],
        'answer': (
            'Agricultural Finance Options — Zimbabwe 2024:\n\n'
            '1. Agribank (Agricultural Bank of Zimbabwe):\n'
            '   - Government-owned bank dedicated to agriculture\n'
            '   - Products: seasonal crop loans, livestock loans, equipment finance\n'
            '   - Minimum smallholder loan: from USD 500\n'
            '   - Interest: approximately 8-15% per annum on USD loans\n'
            '   - Requirements: National ID, land documentation, simple business plan\n'
            '   - Branches: Harare, Bulawayo, Mutare, Gweru, Masvingo, Bindura, Marondera\n'
            '   - Website: www.agribank.co.zw\n\n'
            '2. CBZ Agro-Yield:\n'
            '   - Seasonal crop financing from CBZ Bank\n'
            '   - Requires land collateral or asset security\n\n'
            '3. SMEDCO:\n'
            '   - Loans for agri-processing and value addition businesses\n'
            '   - Useful for poultry units, grinding mills, irrigation setup\n\n'
            '4. Village Savings and Loan Associations (VSLAs):\n'
            '   - No collateral required\n'
            '   - Good for very small amounts: USD 50-500\n'
            '   - Contact your nearest NGO or AGRITEX to find local groups\n\n'
            'Preparation tip: Write a simple one-page plan showing expected farming '
            'costs and projected income before approaching any lender. '
            'This greatly improves your chance of approval.'
        )
    },

    'irrigation_options': {
        'keywords': [
            'irrigation', 'drip irrigation', 'watering crops', 'water crops',
            'small scale irrigation', 'pump', 'borehole', 'irrigation scheme',
            'winter cropping', 'off season farming', 'water access',
            'solar pump', 'treadle pump', 'zinwa',
        ],
        'answer': (
            'Irrigation Options for Smallholder Farmers — Zimbabwe:\n\n'
            'Low-cost options:\n\n'
            '1. Gravity-fed drip irrigation kits:\n'
            '   - Cost: USD 80-300 for a kit covering 200-500m2\n'
            '   - Suppliers: Netafim, iDE Zimbabwe, Farm & City Centre\n'
            '   - Some NGOs distribute subsidised kits — ask AGRITEX or district office\n\n'
            '2. Treadle pump:\n'
            '   - Foot-powered, draws water from shallow wells or streams\n'
            '   - Cost: USD 50-120\n'
            '   - Can irrigate up to 0.5 hectares effectively\n\n'
            '3. Solar-powered pumps:\n'
            '   - Growing availability across Zimbabwe\n'
            '   - Cost: USD 800-3,000 for a complete borehole system\n'
            '   - Some NGO and government programmes offer subsidies\n\n'
            'Government irrigation support:\n'
            '- ZINWA manages dams and canal irrigation schemes\n'
            '- Many communal irrigation schemes in Manicaland, Mashonaland East\n'
            '- Contact District Development Fund (DDF) for rehabilitation assistance\n\n'
            'What to grow in dry season (April-September) with irrigation:\n'
            '- Tomatoes, onions, cabbages, potatoes, beans, wheat\n'
            '- Leafy vegetables year-round: rape, chomolia, spinach\n\n'
            'Even a 0.1 hectare irrigated garden can generate USD 300-800 per season '
            'and keep income flowing through the dry months.'
        )
    },

    'climate_smart_varieties_2024': {
        'keywords': [
            'drought tolerant variety', 'drought resistant seed', 'best seed 2024',
            'drought tolerant maize', 'heat tolerant crop', 'sc403', 'sc647',
            'zim seeds', 'seed co', 'best variety drought', 'which seed buy',
            'zm309', 'open pollinated', 'opv seed', 'certified seed',
        ],
        'answer': (
            'Drought-Tolerant and Climate-Smart Varieties — Zimbabwe 2024/25:\n\n'
            'Maize (drought-tolerant options):\n'
            '- SC403:        90-day, performs well in dry conditions, best for NR III-V\n'
            '- SC647:        Medium maturity, good drought tolerance, NR II-IV\n'
            '- ZM309:        Open-pollinated (OPV), affordable, drought-tolerant\n'
            '- PAN 413:      Short-season, good for drier southern areas\n'
            '- Drought TEGO: Specifically bred for El Nino-type seasons (SeedCo)\n\n'
            'Sorghum (excellent for dry regions):\n'
            '- SV2, SV4: Widely grown in Matabeleland and Masvingo\n'
            '- Macia: Popular dual-purpose variety (food and livestock feed)\n\n'
            'Pearl millet:\n'
            '- SDMV 89508: Fast-maturing, very drought-tolerant\n'
            '- Best for Natural Regions IV and V\n\n'
            'Cowpeas / Nyemba:\n'
            '- Great for dry areas; also fixes nitrogen in the soil\n'
            '- IT18 and Kadode varieties popular in Zimbabwe\n\n'
            'Where to buy certified seed:\n'
            '- SeedCo outlets (nationwide), Agrifoods, Agricura\n'
            '- Farmers World, Farm & City Centre\n'
            '- Government distribution points under Pfumvudza programme\n\n'
            'Warning: Avoid uncertified or recycled seed — germination rates '
            'are unpredictable and yields can be 30-50% lower than certified seed.'
        )
    },

    'mbare_musika_market': {
        'keywords': [
            'mbare musika', 'mbare market', 'sell vegetables', 'vegetable market',
            'market prices vegetables', 'where sell produce', 'market harare',
            'sell tomatoes', 'sell onions', 'produce market', 'wholesale market',
            'vegetable prices harare', 'market prices 2024',
        ],
        'answer': (
            'Mbare Musika — Zimbabwe\'s Main Agricultural Market:\n\n'
            'Overview:\n'
            '- Located in Mbare, Harare — the largest produce market in Zimbabwe\n'
            '- Open 7 days a week; busiest from 4am to 10am\n'
            '- Wholesale and retail: vegetables, fruits, grains, livestock\n\n'
            'Approximate wholesale prices (2024 — vary by season):\n'
            '- Tomatoes:          USD 8-20 per 20kg crate (highest in dry season)\n'
            '- Onions:            USD 15-25 per 50kg bag\n'
            '- Cabbages:          USD 0.30-0.80 each\n'
            '- Leafy veg (rape):  USD 0.20-0.40 per bundle\n'
            '- Potatoes:          USD 25-45 per 50kg bag\n'
            '- Butternuts:        USD 0.50-1.00 each\n'
            '- Green mealies:     USD 0.10-0.20 each (peak season)\n\n'
            'Tips for selling at Mbare:\n'
            '1. Arrive early — prices drop significantly after 9am\n'
            '2. Grade your produce — well-sorted, clean produce gets better prices\n'
            '3. Build relationships with regular buyers for consistent sales\n'
            '4. Pool transport with neighbours to cut haulage costs\n\n'
            'Other market options:\n'
            '- Sakubva market (Mutare), Mkoba market (Gweru), Kudzanai (Masvingo)\n'
            '- TM Pick n Pay and OK Zimbabwe have smallholder supplier programmes\n'
            '- Hotels, lodges, and schools pay premium for consistent quality supply'
        )
    },

    'currency_exchange_2024': {
        'keywords': [
            'exchange rate', 'usd to zig', 'zig rate', 'zimbabwe dollar', 'zwl',
            'currency rate', 'official rate', 'parallel rate', 'how much usd',
            'foreign currency', 'rbz rate', 'zimbabwe gold', 'zig currency',
            'money 2024', 'local currency farming',
        ],
        'answer': (
            'Zimbabwe Currency — 2024 Update:\n\n'
            'Zimbabwe Gold (ZiG):\n'
            '- Zimbabwe introduced ZiG (Zimbabwe Gold) in April 2024\n'
            '- ZiG replaced the Zimbabwe dollar (ZWL) as the official local currency\n'
            '- Backed by gold reserves and foreign currency held by the RBZ\n\n'
            'Exchange rate (approximate as at mid-2024):\n'
            '- Official RBZ rate: approximately 13-14 ZiG per USD 1\n'
            '- Rates change regularly — always verify at your bank or on www.rbz.co.zw\n\n'
            'What this means for farmers:\n'
            '- Most farm inputs (fertiliser, seed, chemicals) are priced in USD\n'
            '- GMB payments may be in USD or ZiG equivalent — confirm before selling\n'
            '- Negotiate and agree on currency before finalising any crop sale\n'
            '- Keep records of all transactions in both currencies\n\n'
            'Important: Currency policy in Zimbabwe changes frequently. '
            'Always confirm the current rate with your bank or Agribank before '
            'making large financial decisions.'
        )
    },

    'fall_armyworm': {
        'keywords': [
            'fall armyworm', 'armyworm', 'caterpillar maize', 'maize pest 2024',
            'army worm', 'maize worm', 'pest outbreak', 'maize leaves eaten',
            'crop pest', 'maize pest control', 'spodoptera', 'worm in maize',
            'maize caterpillar', 'faw',
        ],
        'answer': (
            'Fall Armyworm (FAW) — What Zimbabwean Farmers Need to Know:\n\n'
            'About FAW:\n'
            '- Scientific name: Spodoptera frugiperda\n'
            '- Present in Zimbabwe every season since first arriving around 2016\n'
            '- Primary host: maize. Also attacks sorghum and other cereals\n\n'
            'How to identify early:\n'
            '- "Window-pane" transparent patches on young leaves\n'
            '- Frass (brown pellet droppings) visible in the plant whorl\n'
            '- Caterpillars have a distinctive inverted "Y" shape on the head\n'
            '- Irregular ragged holes in leaves as caterpillars grow larger\n\n'
            'When to treat:\n'
            '- Scout your field twice a week from crop emergence\n'
            '- Act when more than 5 caterpillars per 10 plants or 20% plants damaged\n\n'
            'Control options:\n'
            '1. Emamectin benzoate (e.g. Escort, Proclaim) — most effective chemical\n'
            '2. Chlorpyrifos + cypermethrin (e.g. Duduthrin, Karate)\n'
            '3. Spinosad (Tracer) — effective and more environmentally friendly\n'
            '4. Plant early to reduce peak FAW pressure\n'
            '5. Push-pull intercropping (Desmodium + Napier grass) reduces FAW naturally\n\n'
            'Safety: Always wear gloves, mask, and eye protection when spraying.\n'
            'AGRITEX provides free FAW monitoring and advisory support — '
            'contact your local extension officer at first signs of infestation.'
        )
    },

    'cotton_farming': {
        'keywords': [
            'cotton', 'grow cotton', 'cotton farming', 'cotton price', 'sell cotton',
            'cotton seed', 'cotton yield', 'cotton contract', 'csc cotton',
        ],
        'answer': (
            'Cotton Farming in Zimbabwe:\n\n'
            'Cotton is an important cash crop for Natural Regions III-V '
            '(semi-arid areas of Mashonaland West, Midlands, Matabeleland).\n\n'
            'Growing basics:\n'
            '- Plant in mid-November to early December with the rains\n'
            '- Spacing: 90cm rows x 30cm between plants\n'
            '- Fertiliser: Compound L at planting (low nitrogen, high phosphorus)\n'
            '- Common pests: bollworm, aphids, whitefly — monitor weekly and spray early\n\n'
            '2024 producer prices (approximate):\n'
            '- Seed cotton Grade A: USD 0.50-0.60 per kg\n'
            '- Grade B: USD 0.40-0.50 per kg\n\n'
            'Contract farming:\n'
            '- Cottco and Cargill are the main contractors in Zimbabwe\n'
            '- They provide seed, chemicals, and extension support on credit\n'
            '- Inputs repaid from cotton sale proceeds\n\n'
            'Contact the Cotton Company of Zimbabwe (Cottco) or your nearest '
            'AGRITEX office to register as a contract cotton grower.'
        )
    },

    'soyabean_farming': {
        'keywords': [
            'soyabean', 'soya bean', 'soybeans', 'grow soya', 'soyabean farming',
            'soyabean price', 'soya yield', 'soya varieties',
        ],
        'answer': (
            'Soyabean Farming in Zimbabwe:\n\n'
            'Soyabeans are a high-value crop with strong local and export demand '
            'for stockfeed, cooking oil, and protein meal.\n\n'
            'Growing guide:\n'
            '- Plant: mid-November to mid-December with the rains\n'
            '- Varieties: Soprano, Lanka, SCS1, Pan 1867\n'
            '- Spacing: 45cm rows x 5-7cm between seeds\n'
            '- Seed treatment: inoculate with Rhizobium before planting to boost '
            'nitrogen fixation — reduces need for nitrogen fertiliser\n'
            '- Fertiliser: Compound L at planting (no nitrogen top-dressing needed)\n'
            '- Harvest: 100-120 days when pods turn brown and rattle\n\n'
            '2024 prices:\n'
            '- GMB price: USD 600 per tonne\n'
            '- Private buyers: USD 550-700 per tonne\n'
            '- Good yields: 2-3 tonnes per hectare in favourable conditions\n\n'
            'Rotation benefit: Plant after maize to break disease cycles and improve '
            'soil nitrogen for the next maize crop.\n\n'
            'Buyers: GMB, National Foods, Olivine Industries, private oil pressers.'
        )
    },

    'food_security_programmes': {
        'keywords': [
            'food aid', 'wfp food', 'food assistance', 'hunger programme',
            'food relief', 'wfp zimbabwe', 'world food programme', 'food handout',
            'zimvac', 'food insecurity programme', 'emergency food', 'food crisis help',
        ],
        'answer': (
            'Food Security Assistance in Zimbabwe (2024):\n\n'
            'Following the 2023/24 El Nino disaster declaration, several '
            'programmes are active to support food-insecure households:\n\n'
            '1. World Food Programme (WFP) Zimbabwe:\n'
            '   - Emergency food transfers to affected provinces\n'
            '   - Eligibility based on ZIMVAC assessment data\n'
            '   - Contact your local District Social Welfare Office\n\n'
            '2. Government / GMB grain distribution:\n'
            '   - Subsidised or free grain in drought-affected areas\n'
            '   - Check with your ward councillor or village headman\n\n'
            '3. Pfumvudza/Intwasa Inputs:\n'
            '   - Free seed and fertiliser for the next season\n'
            '   - Register through AGRITEX before the October cutoff\n\n'
            '4. NGO support:\n'
            '   - Catholic Relief Services, World Vision, CARE, Plan International '
            'all have active programmes in Zimbabwe\n'
            '   - Check at your District Development Fund (DDF) office\n\n'
            'Eligibility for food assistance is determined at community level. '
            'Speak to your village head, ward councillor, or district social welfare officer.'
        )
    },
}


# ─────────────────────────────────────────────────────────────
# Topics that bypass the skip_words filter so farmers always
# get current Zimbabwe-specific data for these queries.
# ─────────────────────────────────────────────────────────────
STATS_TOPICS = {
    'maize_production_stats',
    'tobacco_stats',
    'fertiliser_prices',
    'grain_prices',
    'el_nino_drought_2024',
    'rainfall_forecast_2025',
    'government_input_schemes',
    'livestock_prices_2024',
    'agribank_loans',
    'irrigation_options',
    'climate_smart_varieties_2024',
    'mbare_musika_market',
    'currency_exchange_2024',
    'fall_armyworm',
    'cotton_farming',
    'soyabean_farming',
    'food_security_programmes',
}


def get_local_answer(user_message):
    """Check if the question matches our local knowledge base.
    Stats/current-info topics bypass skip_words so farmers always
    get up-to-date Zimbabwe-specific answers for those queries.
    """
    message_lower = user_message.lower()

    # Words that suggest the question is complex enough to benefit
    # from the full Groq response for agronomic how-to topics.
    skip_words = [
        'how much', 'how many', 'what was', 'what is the',
        'statistics', 'stats', 'yield', 'production',
        'price', 'cost', 'last year', 'this year',
        'compare', 'difference', 'best', 'worst',
        'why', 'explain why', 'reason',
        'history', 'record', 'data', 'number',
        'percentage', 'average', 'total',
        'government', 'policy', 'law',
        'forecast', 'predict', 'future',
        'problem', 'issue', 'challenge',
    ]

    # Score every topic
    best_match = None
    best_score = 0
    best_topic = None

    for topic, data in LOCAL_KNOWLEDGE.items():
        score = sum(1 for keyword in data['keywords'] if keyword in message_lower)
        if score > best_score:
            best_score = score
            best_match = data['answer']
            best_topic = topic

    # Stats/current-info topics: return immediately on any keyword match
    if best_score >= 1 and best_topic in STATS_TOPICS:
        return best_match

    # Agronomic how-to topics: apply the original conservative filters
    for word in skip_words:
        if word in message_lower:
            return None

    if len(user_message.split()) > 12:
        return None

    if best_score >= 2:
        return best_match

    return None


def get_ai_response(user_message, conversation_history=None):
    """
    Get a response from the AI.
    First checks local knowledge, then falls back to Groq API.
    """

    local_answer = get_local_answer(user_message)
    if local_answer:
        return {
            'response': local_answer,
            'source': 'local'
        }

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT}
        ]

        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

        messages.append({
            'role': 'user',
            'content': user_message
        })

        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )

        return {
            'response': response.choices[0].message.content,
            'source': 'groq'
        }

    except Exception as e:
        print(f'GROQ ERROR: {type(e).__name__}: {e}')
        return {
            'response': (
                'I am having trouble connecting to my knowledge base right now. '
                'Here are some things you can try:\n\n'
                '1. Ask your question in the Community Forum where other farmers can help\n'
                '2. Contact your local AGRITEX extension officer\n'
                '3. Try asking me again in a few moments\n\n'
                'I apologise for the inconvenience.'
            ),
            'source': 'fallback'
        }