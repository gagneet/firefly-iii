-- Firefly III Subscriptions Import
-- Generated: 2025-10-05
-- User ID: 1, User Group ID: 1
-- Currencies: USD(12), AUD(17), INR(26), CHF(28)

-- IEEE
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'IEEE', 'IEEE', 240.25, 240.25, '2004-03-01', '2024-12-30', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Membership No: 41617804\nPricing: USD $240.25/year, $11.47/month\nAccount: 41617804\nStart Date: 1/03/2004', NOW(), NOW());

-- ACM
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'ACM', 'ACM', 303.00, 303.00, '2004-03-01', '2025-03-31', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Membership No: 0970277\nPricing: USD $303.00/year, $14.46/month\nAccount: 0970277\nStart Date: 1/03/2004', NOW(), NOW());

-- ACS Australian
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'ACS (Australian Computer Society)', 'ACS', 374.00, 374.00, '2018-08-12', '2024-06-29', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Membership No: 4190281\nPricing: AUD $374.00/year\nAccount: 4190281\nStart Date: 12/08/2018', NOW(), NOW());

-- JetBrains
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'JetBrains', 'JetBrains', 190.30, 190.30, '2016-07-14', '2026-07-14', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Membership No: 2LKXV288BS\nPricing: USD $190.30/year, $9.08/month\nAccount: 2LKXV288BS\nStart Date: 14/07/2016', NOW(), NOW());

-- PluralSight
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'PluralSight', 'PluralSight', 295.90, 295.90, '2024-02-12', '2025-02-11', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $295.90/year, $14.12/month\nAccount: gagneet@gmail.com\nStart Date: 12/02/2024', NOW(), NOW());

-- GitHub
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'GitHub', 'GitHub', 48.00, 48.00, '2023-01-31', '2024-01-31', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $48.00/year, $2.29/month\nAccount: gagneet@gmail.com\nStart Date: 31/01/2023', NOW(), NOW());

-- Docker Hub
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'Docker Hub', 'Docker', 60.00, 60.00, '2024-08-20', '2025-08-20', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $60.00/year, $2.86/month\nAccount: gagneet\nStart Date: 20/08/2024', NOW(), NOW());

-- Cybrary
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'Cybrary, Inc. (Security Learning)', 'Cybrary', 324.50, 324.50, '2024-01-04', '2025-01-03', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $324.50/year, $15.49/month\nAccount: gagneet@gmail.com\nStart Date: 4/01/2024', NOW(), NOW());

-- Flickr
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'Flickr', 'Flickr', 71.88, 71.88, '2022-09-07', '2024-09-06', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $71.88/year, $3.43/month\nAccount: gagneet@gmail.com\nStart Date: 7/09/2022', NOW(), NOW());

-- Sensibo Plus
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Sensibo Plus (Annual)', 'Sensibo', 39.99, 39.99, '2024-03-05', '2025-03-05', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $39.99/year\nAccount: avneetrooprai@gmail.com\nStart Date: 5/03/2024', NOW(), NOW());

-- GitKraken
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'GitKraken AxoSoft', 'GitKraken', 52.80, 52.80, '2024-08-02', '2025-08-02', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $52.80/year, $2.52/month\nAccount: gagneet@gmail.com\nStart Date: 2/08/2024', NOW(), NOW());

-- TechSmith SnagIt
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'TechSmith SnagIt', 'SnagIt', 18.84, 18.84, '2023-09-22', '2024-09-21', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $18.84/year\nStart Date: 22/09/2023', NOW(), NOW());

-- YouTube (Monthly)
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Google YouTube Premium', 'YouTube', 16.99, 16.99, '2016-08-16', NULL, 'monthly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $16.99/month\nStart Date: 16/08/2016\nNote: No end date - ongoing subscription', NOW(), NOW());

-- Netflix (INR)
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 26, 'Netflix', 'Netflix', 499.00, 499.00, '2013-01-01', NULL, 'monthly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: INR ₹499.00/month\nStart Date: 1/01/2013\nNote: No end date - ongoing subscription', NOW(), NOW());

-- Stan
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Stan', 'Stan', 0.00, 0.00, '2016-04-06', NULL, 'monthly', 0, 1, 0, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $0.00/month (possibly included or paused)\nStart Date: 6/04/2016\nNote: No end date - inactive', NOW(), NOW());

-- Disney+
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Disney+', 'Disney', 139.99, 139.99, '2024-09-05', '2025-09-05', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $139.99/year\nStart Date: 5/09/2024', NOW(), NOW());

-- Max / HBO
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Max / HBO', 'Max|HBO', 119.99, 119.99, '2025-04-02', '2026-04-02', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $119.99/year\nStart Date: 2/04/2025', NOW(), NOW());

-- Audible AU
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Audible AU', 'Audible', 164.50, 164.50, '2023-12-09', '2024-12-08', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $164.50/year\nStart Date: 9/12/2023', NOW(), NOW());

-- Amazon Prime AU
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Amazon Prime AU', 'Amazon Prime', 79.00, 79.00, '2024-10-01', '2026-10-01', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $79.00/year\nStart Date: 1/10/2024', NOW(), NOW());

-- Binge
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Binge', 'Binge', 0.00, 0.00, '2023-01-01', NULL, 'monthly', 0, 1, 0, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $0.00/month (possibly included or paused)\nStart Date: 1/01/2023\nNote: No end date - inactive', NOW(), NOW());

-- Paramount+
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Paramount+', 'Paramount', 0.00, 0.00, '2022-12-21', '2025-12-21', 'yearly', 0, 1, 0, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $0.00/year (possibly included or paused)\nStart Date: 21/12/2022\nNote: Inactive subscription', NOW(), NOW());

-- Google One Storage
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Google One (Storage)', 'Google One', 124.99, 124.99, '2024-05-14', '2025-05-14', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $124.99/year\nStart Date: 14/05/2024', NOW(), NOW());

-- TripIt
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'TripIt Pro', 'TripIt', 49.00, 49.00, '2024-04-16', '2025-04-16', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $49.00/year, $2.34/month\nAccount: gagneet@gmail.com\nStart Date: 16/04/2024', NOW(), NOW());

-- LinkedIn Preeti
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 26, 'LinkedIn Premium (Preeti)', 'LinkedIn', 1849.99, 1849.99, '2022-06-22', NULL, 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: INR ₹1,849.99/year, AUD $1.01/month equivalent\nStart Date: 22/06/2022\nNote: No end date - ongoing subscription', NOW(), NOW());

-- ProtonMail & Proton VPN
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 28, 'ProtonMail & Proton VPN', 'Proton', 273.86, 273.86, '2024-10-13', '2026-10-14', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: CHF 273.86/year, AUD $15.34/month equivalent\nStart Date: 13/10/2024', NOW(), NOW());

-- Medium
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'Medium', 'Medium', 0.00, 0.00, '2023-09-15', '2024-09-14', 'yearly', 0, 1, 0, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $0.00 (free or paused)\nStart Date: 15/09/2023\nNote: Inactive subscription', NOW(), NOW());

-- The Canberra Times
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'The Canberra Times', 'Canberra Times', 187.00, 187.00, '2024-01-08', '2025-01-07', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $187.00/year\nStart Date: 8/01/2024', NOW(), NOW());

-- Land Rover Here.com Maps
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Land Rover Here.com Maps Update', 'Land Rover|Here.com', 79.67, 79.67, '2022-10-12', '2025-10-12', 'half-year', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $79.67/year\nStart Date: 12/10/2022\nNote: 3-year subscription', NOW(), NOW());

-- ALDI Data Card
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'ALDI Data Card for Land Rover', 'ALDI.*Land Rover', 95.00, 95.00, '2024-02-17', '2025-02-16', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Membership No: 0493380668\nPricing: AUD $95.00/year\nAccount: 0493380668\nStart Date: 17/02/2024', NOW(), NOW());

-- Office 365 Silverfox
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 12, 'Office 365 (Silverfox Technologies)', 'Office 365|Microsoft 365', 108.24, 108.24, '2024-05-26', '2025-05-26', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: USD $108.24/year, $5.17/month\nAccount: gagneet@silverfoxtechnologies.com.au\nStart Date: 26/05/2024', NOW(), NOW());

-- Squarespace avneetrooprai.com
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Squarespace (avneetrooprai.com)', 'Squarespace.*avneetrooprai', 19.80, 19.80, '2024-09-20', '2026-09-20', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $19.80/year\nDomain: avneetrooprai.com\nStart Date: 20/09/2024', NOW(), NOW());

-- Squarespace gagneet.com
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Squarespace (gagneet.com)', 'Squarespace.*gagneet', 29.70, 29.70, '2024-03-08', '2025-03-08', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $29.70/year\nDomain: gagneet.com\nStart Date: 8/03/2024', NOW(), NOW());

-- Squarespace baldevs.com
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Squarespace (baldevs.com)', 'Squarespace.*baldevs', 19.80, 19.80, '2024-03-08', '2025-03-08', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $19.80/year\nDomain: baldevs.com\nStart Date: 8/03/2024', NOW(), NOW());

-- GoDaddy technofabinnovations.co.in (first entry)
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'GoDaddy (technofabinnovations.co.in) - Domain', 'GoDaddy.*technofab', 24.45, 24.45, '2024-04-30', '2025-04-30', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $24.45/year\nDomain: technofabinnovations.co.in\nService: Domain Registration\nStart Date: 30/04/2024', NOW(), NOW());

-- GoDaddy technofabinnovations.co.in (second entry - hosting)
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'GoDaddy (technofabinnovations.co.in) - Hosting', 'GoDaddy.*technofab.*hosting', 206.73, 206.73, '2024-05-29', '2025-05-29', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $206.73/year\nDomain: technofabinnovations.co.in\nService: Web Hosting\nStart Date: 29/05/2024', NOW(), NOW());

-- GoDaddy eastgateresidences.com.au
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'GoDaddy (eastgateresidences.com.au)', 'GoDaddy.*eastgate', 21.77, 21.77, '2024-01-10', '2027-01-09', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $21.77/year\nDomain: eastgateresidences.com.au\nStart Date: 10/01/2024\nNote: 3-year registration', NOW(), NOW());

-- GoDaddy silverfoxtechnologies.com.au
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'GoDaddy (silverfoxtechnologies.com.au)', 'GoDaddy.*silverfox', 21.77, 21.77, '2024-02-16', '2025-02-15', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $21.77/year\nDomain: silverfoxtechnologies.com.au\nStart Date: 16/02/2024', NOW(), NOW());

-- Google Workspaces Skillsapien
INSERT INTO bills (user_id, user_group_id, transaction_currency_id, name, `match`, amount_min, amount_max, date, end_date, repeat_freq, skip, automatch, active, created_at, updated_at)
VALUES (1, 1, 17, 'Google Workspaces (4 Emails - Skillsapien)', 'Google Workspace.*Skillsapien', 443.51, 443.51, '2023-04-01', '2026-04-01', 'yearly', 0, 1, 1, NOW(), NOW());
INSERT INTO notes (noteable_id, noteable_type, text, created_at, updated_at)
VALUES (LAST_INSERT_ID(), 'FireflyIII\\Models\\Bill', 'Pricing: AUD $443.51/year\nService: 4 email accounts\nOrganization: Skillsapien\nStart Date: 1/04/2023', NOW(), NOW());
