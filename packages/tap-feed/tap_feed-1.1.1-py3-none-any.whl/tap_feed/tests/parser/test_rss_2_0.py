"""Tests parsing of Atom 2.0 feed."""

from datetime import timedelta
import json
from typing import List

import pytest
from singer_sdk.tap_base import Tap

from tap_feed.tap import TapFeed


mock_feed_text = """
<rss xmlns:media="http://search.yahoo.com/mrss/" version="2.0">
<channel>
<title>Yahoo News - Latest News & Headlines</title>
<link>https://www.yahoo.com/news</link>
<description>The latest news and headlines from Yahoo! News. Get breaking news stories and in-depth coverage with videos and photos.</description>
<language>en-US</language>
<copyright>Copyright (c) 2021 Yahoo! Inc. All rights reserved</copyright>
<pubDate>Mon, 18 Oct 2021 21:51:11 -0400</pubDate>
<ttl>5</ttl>
<image>
<title>Yahoo News - Latest News & Headlines</title>
<link>https://www.yahoo.com/news</link>
<url>http://l.yimg.com/rz/d/yahoo_news_en-US_s_f_p_168x21_news.png</url>
</image>
<item>
<title>Bourbon producer signals intent to hire replacement workers</title>
<link>https://news.yahoo.com/bourbon-producer-signals-intent-hire-001239666.html</link>
<pubDate>2021-10-19T00:12:39Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">bourbon-producer-signals-intent-hire-001239666.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/bQxGjFE1TwiyDzqkFV23.A--~B/aD00NDgwO3c9NjcyMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/0440905775f152847bd84da925dfb9c0" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Kourtney Kardashian's massive engagement ring from Travis Barker is estimated to be worth $1 million</title>
<link>https://news.yahoo.com/kourtney-kardashians-massive-engagement-ring-164820709.html</link>
<pubDate>2021-10-18T16:48:20Z</pubDate>
<source url="https://www.insider.com/">INSIDER</source>
<guid isPermaLink="false">kourtney-kardashians-massive-engagement-ring-164820709.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/TEE8HwWjJmEU8Wi5dvBQTA--~B/aD0yMjQ5O3c9MzAwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/insider_articles_922/6b1bb0395ffbda90c1c3b24cb56da3c1" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Some Hooters servers on TikTok are saying new shorts are too short</title>
<link>https://news.yahoo.com/hooters-servers-tiktok-saying-shorts-164238995.html</link>
<pubDate>2021-10-17T15:46:31Z</pubDate>
<source url="https://www.nbcnews.com/">NBC News</source>
<guid isPermaLink="false">hooters-servers-tiktok-saying-shorts-164238995.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/6vXR7lxTgXTsUWvDby2_pA--~B/aD0xMjQ5O3c9MjQ5ODthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/nbc_news_122/e975b6d39d3ac2c4de2409bbe5fcc15c" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Train riders held up phones as woman was raped, police say</title>
<link>https://news.yahoo.com/train-riders-held-phones-woman-233116677.html</link>
<pubDate>2021-10-18T23:31:16Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">train-riders-held-phones-woman-233116677.html</guid>
<media:credit role="publishing company"/>
</item>
<item>
<title>Greta Thunberg 'Rickrolls' audience and busts out dance moves during climate concert</title>
<link>https://news.yahoo.com/greta-thunberg-rickrolls-audience-busts-234600985.html</link>
<pubDate>2021-10-18T23:46:00Z</pubDate>
<source url="https://www.washingtonexaminer.com/">Washington Examiner</source>
<guid isPermaLink="false">greta-thunberg-rickrolls-audience-busts-234600985.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/KWKJmcqQLcVrt1pIPbM7ag--~B/aD05NDA7dz0xNTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/washington_examiner_articles_265/23355ebe298e81c51a4c72cad15200ce" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>‘It was about to go down.’ Brawl at Panthers-Vikings game goes viral following tweet</title>
<link>https://news.yahoo.com/down-brawl-panthers-vikings-game-192316380.html</link>
<pubDate>2021-10-18T19:23:16Z</pubDate>
<source url="https://www.charlotteobserver.com/">Charlotte Observer</source>
<guid isPermaLink="false">down-brawl-panthers-vikings-game-192316380.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/Gc0DOSDl7ovZtHXs6HerrA--~B/aD0xNTU1O3c9MTE0MDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/charlotte_observer_mcclatchy_513/34d785311ddc07a6863a5564fa3506cb" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Woman denied organ transplant over refusal to get COVID-19 vaccine</title>
<link>https://news.yahoo.com/woman-denied-organ-transplant-over-170803360.html</link>
<pubDate>2021-10-18T17:08:03Z</pubDate>
<source url="https://www.cbsnews.com/videos/">CBS News Videos</source>
<guid isPermaLink="false">woman-denied-organ-transplant-over-170803360.html</guid>
<media:content height="86" url="https://s.yimg.com/hd/cp-video-transcode/prod/2021-10/18/616dadb89fbf3327ba0536a1/616dadb89fbf3327ba0536a2_o_U_v2.jpg" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Couple vocally opposed to vaccine die of COVID two weeks apart</title>
<link>https://news.yahoo.com/couple-vocally-opposed-vaccine-die-182558816.html</link>
<pubDate>2021-10-18T18:25:58Z</pubDate>
<source url="https://thegrio.com/">TheGrio</source>
<guid isPermaLink="false">couple-vocally-opposed-vaccine-die-182558816.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/RZXdmwDV_J.72t5VCKgG9g--~B/aD01NzY7dz0xMDI0O2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/thegrio_yahoo_articles_946/e9d356a1bea480073215b3ada130ee4c" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Bill and Melinda Gates seen together for first time since divorce at daughter's wedding</title>
<link>https://news.yahoo.com/bill-melinda-gates-seen-together-152115927.html</link>
<pubDate>2021-10-17T15:21:15Z</pubDate>
<source url="https://www.insider.com/">INSIDER</source>
<guid isPermaLink="false">bill-melinda-gates-seen-together-152115927.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/QZ47DBueI2Nx9WICzaZ04Q--~B/aD0yNjY1O3c9MzU1MzthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/insider_articles_922/0ade083549527ae52983fff7ba26a876" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>California congressional race could help tilt House control</title>
<link>https://news.yahoo.com/california-congressional-race-could-help-230845485.html</link>
<pubDate>2021-10-18T23:08:45Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">california-congressional-race-could-help-230845485.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/27yD_CWPMONZxKVbMQ7_4w--~B/aD0yNzE4O3c9Mzg0MDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/583c927ae9922089f54a2893aa947951" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>'America's Got Talent' shares update on Jonathan Goodwin after accident on set</title>
<link>https://news.yahoo.com/americas-got-talent-shares-jonathan-001011690.html</link>
<pubDate>2021-10-18T00:10:11Z</pubDate>
<source url="https://www.today.com/">TODAY</source>
<guid isPermaLink="false">americas-got-talent-shares-jonathan-001011690.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/1CMQfpU3u5yVBL45kR90Lg--~B/aD0xMjAwO3c9MjQwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/nbc_today_217/0c6b2dd480f2952e574987b61fc6984c" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>A California Construction Worker Asked a Speeding Motorist to Slow Down. He Was Shot Seven Times In Response.</title>
<link>https://news.yahoo.com/california-construction-worker-asked-speeding-123000097.html</link>
<pubDate>2021-10-18T12:30:00Z</pubDate>
<source url="https://atlantablackstar.com/">Atlanta Black Star</source>
<guid isPermaLink="false">california-construction-worker-asked-speeding-123000097.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/KJG_MsXNsb9_u.37UCqLrg--~B/aD0zMzg7dz02MDA7YXBwaWQ9eXRhY2h5b24-/https://media.zenfs.com/en/atlanta_black_star_articles_803/14f9be466b764c4a086a962c2c4fb2b8" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Freed murderer charged in Florida with slaying of single mom</title>
<link>https://news.yahoo.com/freed-murderer-charged-florida-slaying-195851469.html</link>
<pubDate>2021-10-17T19:58:51Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">freed-murderer-charged-florida-slaying-195851469.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/oDLRWX7drNRouaSxmIW07g--~B/aD0xMzg3O3c9MjAwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/9874f811f0df37fd9a6d54f02aea499b" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Fox News anchor John Roberts deleted a tweet that questioned vaccine efficacy in light of Colin Powell's death, clarifying that he is actually pro-vaccine</title>
<link>https://news.yahoo.com/fox-news-anchor-john-roberts-155319063.html</link>
<pubDate>2021-10-18T15:53:19Z</pubDate>
<source url="https://www.businessinsider.com/">Business Insider</source>
<guid isPermaLink="false">fox-news-anchor-john-roberts-155319063.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/Ofb8gK8x6fmUD9i8nSYJ3Q--~B/aD0xMzk4O3c9MTg2MzthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/business_insider_articles_888/e831b7b7b65d5e94f964a73ec8ea644d" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Dennis Prager Announces He Has COVID After Hugging ‘Thousands’ to Get It</title>
<link>https://news.yahoo.com/dennis-prager-announces-covid-hugging-212144657.html</link>
<pubDate>2021-10-18T21:21:44Z</pubDate>
<source url="http://www.thedailybeast.com">The Daily Beast</source>
<guid isPermaLink="false">dennis-prager-announces-covid-hugging-212144657.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/TXxCh_Wk4Qkkx6c84G95Gg--~B/aD02NTg7dz0xMTcwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/thedailybeast.com/487f6b9098e919b703fd498bfc44fa12" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Vaccines, masks? Japan puzzling over sudden virus success</title>
<link>https://news.yahoo.com/vaccines-masks-japan-puzzling-over-034036438.html</link>
<pubDate>2021-10-18T03:40:36Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">vaccines-masks-japan-puzzling-over-034036438.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/ZqA52aMGdS3qprPBbGNQcw--~B/aD0zMzMzO3c9NTAwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/30066b303bf37f3629a8a41e5e45ef56" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>'Eternals' star Salma Hayek says she had 'problems with the script' and 'got into a serious fight' with director Chloé Zhao, but they found 'middle ground'</title>
<link>https://news.yahoo.com/eternals-star-salma-hayek-says-173151941.html</link>
<pubDate>2021-10-18T17:31:51Z</pubDate>
<source url="https://www.insider.com/">INSIDER</source>
<guid isPermaLink="false">eternals-star-salma-hayek-says-173151941.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/cZGes9xdBWLFHuhuBig91Q--~B/aD0xNzE1O3c9MjI4NzthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/insider_articles_922/7740f63b4b412d5735f2e636d95f2e4b" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Eric Stonestreet says it's 'ridiculous' that fans assume he, fiancée have large age gap: 'She looks fantastic'</title>
<link>https://news.yahoo.com/eric-stonestreet-says-apos-apos-213249910.html</link>
<pubDate>2021-10-18T21:32:49Z</pubDate>
<source url="https://www.foxnews.com/">Fox News</source>
<guid isPermaLink="false">eric-stonestreet-says-apos-apos-213249910.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/eNWAvThEdtIpAZ5YjUYdWg--~B/aD03MjA7dz0xMjgwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/fox_news_text_979/b7c5345f1346cc05d1220e909747273c" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Oregon illegal pot grows: More calls to send National Guard</title>
<link>https://news.yahoo.com/oregon-illegal-pot-grows-more-204121840.html</link>
<pubDate>2021-10-18T20:41:21Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">oregon-illegal-pot-grows-more-204121840.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/VzvoC0LW9LgECK.RVtzcXw--~B/aD0xNjYzO3c9MjQ5NDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/f1903c6d5184cf27831d197b0fd4c0b3" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>200 painted, naked models descend on Dead Sea for photo shoot</title>
<link>https://news.yahoo.com/200-painted-naked-models-descend-165700229.html</link>
<pubDate>2021-10-18T16:57:00Z</pubDate>
<source url="https://www.washingtonexaminer.com/">Washington Examiner</source>
<guid isPermaLink="false">200-painted-naked-models-descend-165700229.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/altGL3m0Y38XudH93jSsrQ--~B/aD05NDA7dz0xNTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/washington_examiner_articles_265/435bad37036b277d5ea42276c86189b6" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Trump answered questions for 4 hours in a deposition for a lawsuit alleging his bodyguards beat up protesters outside Trump Tower</title>
<link>https://news.yahoo.com/trump-answered-questions-4-hours-212359653.html</link>
<pubDate>2021-10-18T21:23:59Z</pubDate>
<source url="https://www.businessinsider.com/">Business Insider</source>
<guid isPermaLink="false">trump-answered-questions-4-hours-212359653.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/ZMN2MDisO8RC0iz7pqVvTQ--~B/aD0xMTM3O3c9MTUxNjthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/business_insider_articles_888/07c09df6d9eb34f11bed2a24cf6a0111" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Louisiana gators thrive, so farmers' return quota may drop</title>
<link>https://news.yahoo.com/louisiana-gators-thrive-farmers-return-144731641.html</link>
<pubDate>2021-10-17T14:47:31Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">louisiana-gators-thrive-farmers-return-144731641.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/9qbq6w7xT6JG76JmGkfI1g--~B/aD0yNDc0O3c9MzcxMTthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/d3c366828b6dcd7dd9243819d1e0aa94" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Ted Cruz blasted Australia’s COVID rules. A top Australian official didn’t hold back</title>
<link>https://news.yahoo.com/ted-cruz-blasted-australia-covid-135920141.html</link>
<pubDate>2021-10-18T13:59:20Z</pubDate>
<source url="https://www.star-telegram.com/">Fort Worth Star-Telegram</source>
<guid isPermaLink="false">ted-cruz-blasted-australia-covid-135920141.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/cbY5Lyh4dImFVV8XWQIhMQ--~B/aD02NDE7dz0xMTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/fort_worth_star_telegram_mcclatchy_952/7ada7b1467e3a9b7f9125aacd355732f" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Man charged with assault after prosecutors say he grabbed another parent at a Minnesota school board meeting about masking</title>
<link>https://news.yahoo.com/man-charged-assault-prosecutors-grabbed-220109239.html</link>
<pubDate>2021-10-18T22:01:09Z</pubDate>
<source url="https://www.insider.com/">INSIDER</source>
<guid isPermaLink="false">man-charged-assault-prosecutors-grabbed-220109239.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/yCS8PKcRYy5YlLjDL7BI2A--~B/aD00NjA7dz02MTM7YXBwaWQ9eXRhY2h5b24-/https://media.zenfs.com/en/insider_articles_922/1650d4359777548ee766c2310e835ef3" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Japan PM says Fukushima wastewater release can't be delayed</title>
<link>https://news.yahoo.com/japan-pm-says-fukushima-wastewater-125248800.html</link>
<pubDate>2021-10-17T12:52:48Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">japan-pm-says-fukushima-wastewater-125248800.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/rtyjjFU2VFTuYkcvqxJbkw--~B/aD0zNjQ4O3c9NTQ3MjthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/fb07bd0b7c85b2bcef4bc867b2337668" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>She thought she won $300 — but her lottery ticket was worth much more in South Carolina</title>
<link>https://news.yahoo.com/she-thought-she-won-300-144711801.html</link>
<pubDate>2021-10-18T14:47:11Z</pubDate>
<source url="https://www.thestate.com/">The State</source>
<guid isPermaLink="false">she-thought-she-won-300-144711801.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/28C1HgJiXXx6wrCtFf0RKg--~B/aD03NTk7dz0xMTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/the_state_mcclatchy_264/5b1799ef12d34403009b4f5602a6248d" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Brian Laundrie lookalike claims US Marshals burst into hotel room</title>
<link>https://news.yahoo.com/brian-laundrie-lookalike-claims-us-214200021.html</link>
<pubDate>2021-10-18T21:42:00Z</pubDate>
<source url="https://www.washingtonexaminer.com/">Washington Examiner</source>
<guid isPermaLink="false">brian-laundrie-lookalike-claims-us-214200021.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/T1koH.vRvjOAuCCOJITYdw--~B/aD05NDA7dz0xNTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/washington_examiner_articles_265/0527dcb4a31d7242503aa1fc5b45ce7e" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Philippine forces kill 4 suspected Chinese drug dealers</title>
<link>https://news.yahoo.com/philippine-forces-kill-4-suspected-141403231.html</link>
<pubDate>2021-10-18T14:14:03Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">philippine-forces-kill-4-suspected-141403231.html</guid>
<media:content height="86" url="https://s.yimg.com/os/creatr-uploaded-images/2021-10/b96d2a40-3032-11ec-affc-8609c7aa0cf2" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Jordan Klepper Exposes MAGA Morons Who Still Think ‘Trump Won’</title>
<link>https://news.yahoo.com/jordan-klepper-exposes-maga-morons-010010286.html</link>
<pubDate>2021-10-19T01:00:10Z</pubDate>
<source url="http://www.thedailybeast.com">The Daily Beast</source>
<guid isPermaLink="false">jordan-klepper-exposes-maga-morons-010010286.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/VdarZRwy_nTBNQVg86QxdQ--~B/aD02NTg7dz0xMTcwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/thedailybeast.com/4dba2aa912b7ad864de728d63183758c" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Woman's body recovered from mountain after she sent message for help</title>
<link>https://news.yahoo.com/climbers-body-recovered-mountain-she-125113389.html</link>
<pubDate>2021-10-18T12:51:00Z</pubDate>
<source url="https://www.cbsnews.com/">CBS News</source>
<guid isPermaLink="false">climbers-body-recovered-mountain-she-125113389.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/pYczVCCOcp11IkYZGjudwA--~B/aD02Njc7dz0xMDE4O2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/cbs_news_897/29ac5daa425908dcefa67bbab7920892" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Coast Guard: 1,200-foot ship dragged California oil pipeline</title>
<link>https://news.yahoo.com/coast-guard-1-200-foot-174350385.html</link>
<pubDate>2021-10-17T17:43:50Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">coast-guard-1-200-foot-174350385.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/LqC_25_eISFO.Iqf7BbLZA--~B/aD0yMDAwO3c9MzAwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/c93491e5d1909c4422311dc2e9aa562d" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Brian Laundrie's father was captured removing a yellow protest sign about his daughter from his front yard, report says</title>
<link>https://news.yahoo.com/brian-laundries-father-captured-removing-203330639.html</link>
<pubDate>2021-10-17T20:33:30Z</pubDate>
<source url="https://www.insider.com/">INSIDER</source>
<guid isPermaLink="false">brian-laundries-father-captured-removing-203330639.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/hS7wyUvd4ZokwRXX9VssgQ--~B/aD0xMTA0O3c9MTQ3MzthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/insider_articles_922/10dff734740fcb31cfd070f0ea4c8f94" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Untaming a river: The stakes behind America’s largest dam removal</title>
<link>https://news.yahoo.com/untaming-river-stakes-behind-america-085100296.html</link>
<pubDate>2021-10-18T08:51:00Z</pubDate>
<source url="http://www.csmonitor.com/">Christian Science Monitor</source>
<guid isPermaLink="false">untaming-river-stakes-behind-america-085100296.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/H228Vj0U7RnV5uwPH73BRg--~B/aD02MDA7dz05MDA7YXBwaWQ9eXRhY2h5b24-/https://media.zenfs.com/en/csmonitor.com/b6bee7d951a29248539bd06074fc870c" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>U.S. Supreme Court again protects police accused of excessive force</title>
<link>https://news.yahoo.com/u-supreme-court-again-protects-181825164.html</link>
<pubDate>2021-10-18T18:18:25Z</pubDate>
<source url="https://www.yahoo.com/news">Yahoo News Video</source>
<guid isPermaLink="false">u-supreme-court-again-protects-181825164.html</guid>
<media:content height="86" url="https://s.yimg.com/hd/cp-video-transcode/prod/2021-10/18/616dba72309e6d28efcee16c/616dba72309e6d28efcee16d_o_U_v2.jpg" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Progressive activists demand Rahm Emanuel nomination removal</title>
<link>https://news.yahoo.com/progressive-activists-demand-rahm-emanuel-003332340.html</link>
<pubDate>2021-10-19T00:33:32Z</pubDate>
<source url="https://www.axios.com/">Axios</source>
<guid isPermaLink="false">progressive-activists-demand-rahm-emanuel-003332340.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/jBdnhNwuRyw9ODlwNNth_A--~B/aD03MjA7dz0xMjgwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/axios_articles_623/a799a4907ec9a05cdf1a1d7c048450f6" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Twitter Users Snarkily Respond To Trump's Lawsuit Against Jan. 6 Documents</title>
<link>https://news.yahoo.com/twitter-users-snarkily-respond-trumps-233821581.html</link>
<pubDate>2021-10-18T23:38:21Z</pubDate>
<source url="https://www.huffpost.com">HuffPost</source>
<guid isPermaLink="false">twitter-users-snarkily-respond-trumps-233821581.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/IsMseGCnQQuvxK1p5f_bQA--~B/aD02MDA7dz0xMjAwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/the_huffington_post_584/38fd819ef6dccb38a69fa2de1eb69086" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Gambian Toufah Jallow tells of surviving rape by dictator</title>
<link>https://news.yahoo.com/gambian-toufah-jallow-tells-surviving-082807483.html</link>
<pubDate>2021-10-17T08:28:07Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">gambian-toufah-jallow-tells-surviving-082807483.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/el_vpQQ820Hwglgrlz3wUg--~B/aD0yNDQ3O3c9MTYzMjthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/2a06435c64f90793db5b9c49245f61d1" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>The Suns gave $133 million to 2 role players in 2 days after deciding not to give their No. 1 pick a max contract</title>
<link>https://news.yahoo.com/suns-gave-133-million-2-230339362.html</link>
<pubDate>2021-10-18T23:03:39Z</pubDate>
<source url="https://www.insider.com/">INSIDER</source>
<guid isPermaLink="false">suns-gave-133-million-2-230339362.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/iSdH6Jjs5G1kLF7Gn.p3kQ--~B/aD0xMTY3O3c9MTU1NzthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/insider_articles_922/fa0a21ecd9d6bd68d82c2bc295d19911" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>VIDEO: Deadly floods and landslides sweep away homes in southern India</title>
<link>https://news.yahoo.com/video-deadly-floods-landslides-sweep-211138272.html</link>
<pubDate>2021-10-18T21:11:38Z</pubDate>
<source url="https://www.insider.com/">INSIDER Video</source>
<guid isPermaLink="false">video-deadly-floods-landslides-sweep-211138272.html</guid>
<media:content height="86" url="https://s.yimg.com/hd/cp-video-transcode/prod/2021-10/18/616de44888b0ef282fb698f2/616de44888b0ef282fb698f3_o_U_v2.jpg" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>South Dakota lawmakers summon key figures for Noem inquiry</title>
<link>https://news.yahoo.com/south-dakota-lawmakers-summon-key-175834782.html</link>
<pubDate>2021-10-18T17:58:34Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">south-dakota-lawmakers-summon-key-175834782.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/OiBg8055rqNlCrRI5ppfXg--~B/aD01NjUxO3c9ODQ3NjthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/cdac5ecb2a7dc055078af5769efe6f1a" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Food Network star Anne Burrell gets married: 'Luckiest girl in the world'</title>
<link>https://news.yahoo.com/food-network-star-anne-burrell-150131304.html</link>
<pubDate>2021-10-17T15:01:31Z</pubDate>
<source url="https://www.today.com/">TODAY</source>
<guid isPermaLink="false">food-network-star-anne-burrell-150131304.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/qjG2VogCr.TgaXdEUOUHNQ--~B/aD0xMjAwO3c9MjQwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/nbc_today_217/59a6816d15ece06faf4dc49b48d4eead" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Billionaire ex-Walmart exec says the first 'settlers' of his planned $400 billion city 'Telosa' will likely be selected through applications - and they could move in by 2030</title>
<link>https://news.yahoo.com/billionaire-ex-walmart-exec-says-161647946.html</link>
<pubDate>2021-10-18T16:16:47Z</pubDate>
<source url="https://www.businessinsider.com/">Business Insider</source>
<guid isPermaLink="false">billionaire-ex-walmart-exec-says-161647946.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/hZkVTjRVuUHnHEYJ0ePJ_Q--~B/aD0xNDA1O3c9MTg3NDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/business_insider_articles_888/54e8469678fd23fcf319239e614006f3" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Rare Sumatran tiger found dead in animal trap in Indonesia</title>
<link>https://news.yahoo.com/rare-sumatran-tiger-found-dead-103208001.html</link>
<pubDate>2021-10-18T10:32:08Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">rare-sumatran-tiger-found-dead-103208001.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/nG.nKRCyOqgVch.HikPw0g--~B/aD00MDAxO3c9NjAwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/31097eab8bdc091fb9e59ffac0b93e08" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Trump says he wouldn't need vaccine mandates and would convince people: 'I would sell it'</title>
<link>https://news.yahoo.com/trump-says-wouldnt-vaccine-mandates-200900849.html</link>
<pubDate>2021-10-18T20:09:00Z</pubDate>
<source url="https://www.washingtonexaminer.com/">Washington Examiner</source>
<guid isPermaLink="false">trump-says-wouldnt-vaccine-mandates-200900849.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/.DMVfwKi_LorccSplMjzdg--~B/aD05NDA7dz0xNTQwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/washington_examiner_articles_265/09e613d0c2dd2f9fb72e4e3cfdb77fec" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Paul McCartney opens up about the real woman who inspired 'Eleanor Rigby' and says she 'enriched my soul'</title>
<link>https://news.yahoo.com/paul-mccartney-opens-real-woman-175306632.html</link>
<pubDate>2021-10-18T17:53:06Z</pubDate>
<source url="https://www.insider.com/">INSIDER</source>
<guid isPermaLink="false">paul-mccartney-opens-real-woman-175306632.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/76_7GS0xvcxUzBYefvXkoQ--~B/aD05MDA7dz0xMjAwO2FwcGlkPXl0YWNoeW9u/https://media.zenfs.com/en/insider_articles_922/b9b7a576535d5206b008e16fa5229b75" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Analysis: NFL loaded with mediocre teams 6 weeks into season</title>
<link>https://news.yahoo.com/nfl-loaded-mediocre-poor-teams-071427781.html</link>
<pubDate>2021-10-18T07:14:27Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">nfl-loaded-mediocre-poor-teams-071427781.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/9ZdgmW7NUj7N32fjoWK0Dw--~B/aD00MDAwO3c9NjAwMDthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/ap.org/6d9bdf234dc2db56e85ba723c1489592" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Three dead, including suspect, after man cuts throat of Arkansas officer</title>
<link>https://news.yahoo.com/three-dead-including-suspect-man-223400267.html</link>
<pubDate>2021-10-17T22:34:00Z</pubDate>
<source url="https://www.nbcnews.com/">NBC News</source>
<guid isPermaLink="false">three-dead-including-suspect-man-223400267.html</guid>
<media:credit role="publishing company"/>
</item>
<item>
<title>A Florida school says vaccinated students must stay home for 30 days after each shot, citing a false claim that they'll infect others</title>
<link>https://news.yahoo.com/florida-school-says-students-vaxxed-181722021.html</link>
<pubDate>2021-10-18T17:33:29Z</pubDate>
<source url="https://www.businessinsider.com/">Business Insider</source>
<guid isPermaLink="false">florida-school-says-students-vaxxed-181722021.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/75sQ44WrVwSJSlPW5xJ43w--~B/aD0xMzk4O3c9MTg2OTthcHBpZD15dGFjaHlvbg--/https://media.zenfs.com/en/business_insider_articles_888/311345bdb83ece7c504fd34567562cbf" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Judge denies request to block lethal injection in Alabama</title>
<link>https://news.yahoo.com/judge-denies-request-block-lethal-181058527.html</link>
<pubDate>2021-10-18T18:10:58Z</pubDate>
<source url="http://www.ap.org/">Associated Press</source>
<guid isPermaLink="false">judge-denies-request-block-lethal-181058527.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/gcek8z5gLf.nyagaN_6udg--~B/aD01MzU7dz00NTg7YXBwaWQ9eXRhY2h5b24-/https://media.zenfs.com/en/ap.org/a11d53d22dde44d5b3e6ed3e8529d24d" width="130"/>
<media:credit role="publishing company"/>
</item>
<item>
<title>Republican resistance to Democrats' anti-gerrymandering efforts could lead to a GOP 'takeover'</title>
<link>https://news.yahoo.com/republican-resistance-democrats-anti-gerrymandering-214800354.html</link>
<pubDate>2021-10-18T21:48:00Z</pubDate>
<source url="https://theweek.com/">The Week</source>
<guid isPermaLink="false">republican-resistance-democrats-anti-gerrymandering-214800354.html</guid>
<media:content height="86" url="https://s.yimg.com/uu/api/res/1.2/A881V3VyNNv9IO_zGKcV6g--~B/aD02MTg7dz04NDU7YXBwaWQ9eXRhY2h5b24-/https://media.zenfs.com/en/the_week_574/65ee2726a705662d6433a797c90986e4" width="130"/>
<media:credit role="publishing company"/>
</item>
</channel>
</rss>
"""


class MockResponse:
    status_code = 200
    elapsed = timedelta(seconds=1)
    headers = {}
    url = "https://www.yahoo.com/news/rss"
    text = mock_feed_text


@pytest.mark.parametrize(
    "configuration,expected_record_keys",
    [
        (
            {"feed_urls": ["http://Ill-be-replaced-through-monkeypatch.com"]},
            [
                "feed_url",
                "feed_title",
                "entry_id",
                "entry_published",
                "entry_title",
                "entry_link",
            ],
        ),
        (
            {
                "feed_urls": ["http://Ill-be-replaced-through-monkeypatch.com"],
                "feed_fields": ["title"],
                "feed_entry_fields": ["id", "title", "link"],
            },
            [
                "feed_url",
                "feed_title",
                "entry_id",
                "entry_published",
                "entry_title",
                "entry_link",
            ],
        ),
        (
            {
                "feed_urls": ["http://Ill-be-replaced-through-monkeypatch.com"],
                "feed_fields": ["title"],
                "feed_entry_fields": ["title"],
            },
            [
                "feed_url",
                "feed_title",
                "entry_id",
                "entry_published",
                "entry_title",
            ],
        ),
        (
            {
                "feed_urls": ["http://Ill-be-replaced-through-monkeypatch.com"],
                "feed_fields": ["title", "language"],
                "feed_entry_fields": ["title", "guid", "source"],
            },
            [
                "feed_url",
                "feed_title",
                "feed_language",
                "entry_id",
                "entry_published",
                "entry_title",
                "entry_guid",
                "entry_source",
            ],
        ),
    ],
)
def test_parsing(monkeypatch, capfd, configuration, expected_record_keys):
    """Verifies the feed is parsed as expected"""

    def mock_get(*args, **kwargs):
        return MockResponse()

    test_tap: Tap = TapFeed(config=configuration)
    monkeypatch.setattr(test_tap.streams["feed"]._requests_session, "send", mock_get)

    test_tap.sync_all()
    out, err = capfd.readouterr()
    tap_records = get_parsed_records(out)
    assert len(tap_records) == 50
    for record in tap_records:
        assert record["type"] == "RECORD"
        assert record["stream"] == "feed"
        assert record["record"]["feed_url"] == MockResponse.url
        assert list(record["record"].keys()) == expected_record_keys


def get_parsed_records(tap_output: str) -> List[dict]:
    """Generates a list of the records from the stdout string provided"""
    return [
        json.loads(_ + "}") for _ in tap_output.split("}\n") if '"type": "RECORD' in _
    ]
