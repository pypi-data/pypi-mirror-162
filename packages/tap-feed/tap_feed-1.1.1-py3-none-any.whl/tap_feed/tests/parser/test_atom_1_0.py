"""Tests parsing of Atom 2.0 feed."""

from datetime import timedelta
import json
from typing import List

import pytest
from singer_sdk.tap_base import Tap

from tap_feed.tap import TapFeed


mock_feed_text = """
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<feed xmlns="http://www.w3.org/2005/Atom">
<title>
<![CDATA[ Global Hunger Index (GHI) - peer-reviewed annual publication designed to comprehensively measure and track hunger at the global, regional, and country levels ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org"/>
<subtitle type="html">
<![CDATA[ The Global Hunger Index is a peer-reviewed annual report, jointly published by Concern Worldwide and Welthungerhilfe, designed to comprehensively measure and track hunger at the global, regional, and country levels. The aim of the GHI is to trigger action to reduce hunger around the world. ]]>
</subtitle>
<rights>
<![CDATA[ Copyright 2021, Global Hunger Index (GHI) - peer-reviewed annual publication designed to comprehensively measure and track hunger at the global, regional, and country levels ]]>
</rights>
<updated>2021-10-19T01:28:10+00:00</updated>
<id>urn:uuid:12a48ca2-c77f-568c-f307-0a993066692a</id>
<generator uri="http://www.elxis.org/" version="5.2">Elxis</generator>
<author>
<name>
<![CDATA[ Ethical Sector ]]>
</name>
</author>
<icon>https://www.globalhungerindex.org/media/images/favicon.ico</icon>
<logo>https://www.globalhungerindex.org/media/images/logo_rss.png</logo>
<entry>
<title>
<![CDATA[ Global Hunger Index Scores by 2021 GHI Rank ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/ranking.html"/>
<id>urn:uuid:0e8469c6-d051-2bfe-d50e-befebb7913dc</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles4/mockup-poster_thumb.jpg" alt="Global Hunger Index Scores by 2021 GHI Rank" /> <strong>For the 2021 GHI report, data were assessed for 135 countries. Out of these, there were sufficient data to calculate 2021 GHI scores for and rank 116 countries.</strong><br /> ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles4/mockup-poster_thumb.jpg" length="5553" type="image/jpeg"/>
</entry>
<entry>
<title>
<![CDATA[ Download the Global Hunger Index ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/download/all.html"/>
<id>urn:uuid:e2b4457b-f0a2-236c-ca99-3561c1e065bc</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles/mockup_thumb.jpg" alt="Download the Global Hunger Index" /> <strong>The Global Hunger Index was first produced in 2006. It is published every October. The 2021 edition marks the 16th edition of the GHI.</strong><br /> ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles/mockup_thumb.jpg" length="4174" type="image/jpeg"/>
</entry>
<entry>
<title>
<![CDATA[ Hunger and Food Systems in Conflict Settings ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/issues-in-focus/2021.html"/>
<id>urn:uuid:455fe9b7-f932-e476-b2cd-9d3c8d165394</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles4/essay_thumb.jpg" alt="Hunger and Food Systems in Conflict Settings" /> <strong>Failing food systems and the consequent increase in hunger are among the most pressing issues of our time. The world is falling far short of what is needed to achieve Zero Hunger—the second of the United Nations’ Sustainable Development Goals (SDGs).</strong><br /> Hunger and Food Systems in Conflict Settings &nbsp;&nbsp;&nbsp; By Caroline Delgado and Dan Smith Stockholm International Peace Research Institute October 2021 About image Photo: Welthungerhilfe/Stefanie Glinski 2018; At a village market in South Sudan, a woman sells fruits and vegetables to earn her livelihood. By boosting livelihood security, resilient food systems contribute to peace building. Thus, especially in conflict-affected contexts, local markets play an important role in the recovery of the households of both vendors and consumers. Hide ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles4/essay_thumb.jpg" length="8512" type="image/jpeg"/>
</entry>
<entry>
<title>
<![CDATA[ Policy Recommendations ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/policy-recommendations.html"/>
<id>urn:uuid:1113eed6-c6b5-bbfd-62fa-51c0cd0560be</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles4/policy-recommendations_thumb.jpg" alt="Policy Recommendations" /> <strong>Concern Worldwide and Welthungerhilfe share a mission to eradicate hunger, and produce the GHI every year to track hunger levels around the world, understand progress, and spotlight areas for action.</strong><br /> Policy Recommendations &nbsp; &nbsp; &nbsp;&nbsp;&nbsp; About image Photo: Concern Worldwide/Ollivier Girard 2021; A woman waters vegetables in the communal garden in the village of Toungaïli, Tahoua region, Niger. Climate volatility and conflict directly affect the agricultural livelihoods of thousands of communities. Resilient and climate-smart agriculture is, therefore, key to improving food and nutrition security. Hide header ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles4/policy-recommendations_thumb.jpg" length="9344" type="image/jpeg"/>
</entry>
<entry>
<title>
<![CDATA[ Global, Regional, and National Trends ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/trends.html"/>
<id>urn:uuid:f7dddddb-4664-2c63-de2d-9ee26cc26987</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles4/map_thumb.png" alt="Global, Regional, and National Trends" /> <strong>The fight against hunger is dangerously off track. Based on current GHI projections, the world as a whole - and 47 countries in particular - will fail to achieve a low level of hunger by 2030.</strong><br /> Global, Regional and National Trends &nbsp; &nbsp; &nbsp;&nbsp;&nbsp; About image Photo: Welthungerhilfe 2021; Puja Jatav sieves edible grains at a Nutrition Smart Village, a relief initiative that fosters nutrition-sensitive agriculture, in the village of Haripur, India. People have been severely hit by COVID-19 and by pandemic-related restrictions in India, the country with the highest child wasting rate worldwide. Hide Key Messages The fight against hunger is dangerously off track. Based on current GHI projections, the world as a whole - and 47 countries in particular - will fail to achieve a low level of hunger by 2030. Food security is under assault on multiple fronts. Worsening conflict, weather extremes associated with global climate change, and the economic and health challenges associated with the COVID-19 pandemic are all driving hunger. After decades of decline, the global prevalence of undernourishment - a component of the Global Hunger Index - is increasing. This shift may be a leading indicator of reversals in other measures of hunger. Africa South of the Sahara and South Asia are the world regions where hunger levels are highest. Hunger in both regions is considered serious. Dozens of countries suffer from severe hunger. According to the 2021 GHI scores and provisional designations, drawing on data from 2016–2020, hunger is considered extremely alarming in one country (Somalia), alarming in 9 countries, and serious in 37 countries. Inequality - between regions, countries, districts, and communities - is pervasive and, left unchecked, will keep the world from achieving the Sustainable Development Goal (SDG) mandate to “leave no one behind.” It is difficult to be optimistic about hunger in 2021. The forces now driving hunger are overpowering good intentions and lofty goals. Among the most powerful and toxic of these forces are conflict, climate change, and COVID-19—three Cs that threaten to wipe out any progress that has been made against hunger in recent years. Violent conflict, which is deeply intertwined with hunger, shows no signs of abating. The consequences of climate change are becoming ever more apparent (Masson-Delmotte et al. 2021) and costly, but the world has developed no fully effective mechanism to slow, much less reverse, it (Raiser et al. 2020). And the COVID-19 pandemic, which has spiked in different parts of the world throughout 2020 and 2021, has shown just how vulnerable we are to global contagion and the associated health and economic consequences. As we struggle to contain the current pandemic, we must be realistic that this will not be the last. As a result of these forces—as well as a host of underlying factors such as poverty, inequality, unsustainable food systems, lack of investment in agriculture and rural development, inadequate safety nets, and poor governance—progress in the fight against hunger shows signs of stalling and even being reversed. It is in this dire context that the hunger situation is playing out in the world as a whole, in global regions, and in individual countries. Figure 1.1 WORLD GHI SCORES AND PREVALENCE OF UNDERNOURISHMENT IN RECENT DECADES Note: GHI scores for the year 2000 include data from 1998–2002; 2006 GHI scores include data from 2004–2008; 2012 GHI scores include data from 2010–2014; and 2021 GHI scores include data from 2016–2020. Data on undernourishment are from FAO (2021). The undernourishment values include data from high-income countries with low levels of hunger, which are excluded from the GHI. For a complete list of data sources for the calculation of GHI scores, see Appendix C. ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles4/map_thumb.png" length="26903" type="image/png"/>
</entry>
<entry>
<title>
<![CDATA[ Assessing the Severity of Hunger in Countries with Incomplete Data ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/designations.html"/>
<id>urn:uuid:7b5ceafb-f3f8-93fc-148f-1d2adbfa5e61</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles2/2020-box-1-3_thumb.png" alt="Assessing the Severity of Hunger in Countries with Incomplete Data" /> <strong>In this year’s GHI report, 19 countries that met the criteria for inclusion in the GHI had insufficient data to allow for calculation of a 2021 GHI score.</strong><br /> Box 1.3 ASSESSING THE SEVERITY OF HUNGER IN COUNTRIES WITH INCOMPLETE DATA In this year’s GHI report, 19 countries that met the criteria for inclusion in the GHI had insufficient data to allow for calculation of a 2021 GHI score. To address this gap and give a preliminary picture of hunger in the countries with missing data, the table below indicates provisional designations of the severity of hunger. These designations are based on those GHI indicator values that are available, the country’s last known GHI severity designation, the country’s last known prevalence of undernourishment, the prevalence of undernourishment for the subregion in which the country is located, and/or an examination of the 2019, 2020, and 2021 editions of the Global Report on Food Crises (FSIN 2019; FSIN and GNAFC 2020, 2021). In some cases, data are missing because of violent conflict or political unrest (FAO, IFAD et al. 2017; Martin-Shields and Stojetz 2019), which are strong predictors of hunger and undernutrition (see Box 1.4 and this year's essay). The countries with missing data may often be those facing the greatest hunger burdens. Of the 4 countries provisionally designated as alarming - Burundi, Comoros, South Sudan, and Syrian Arab Republic - it is possible that with complete data, one or more of them would fall into the extremely alarming category. However, without sufficient information to confirm that this is the case, we have conservatively categorized each of these countries as alarming. ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles2/2020-box-1-3_thumb.png" length="16096" type="image/png"/>
</entry>
<entry>
<title>
<![CDATA[ About: The Concept of the Global Hunger Index ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/about.html"/>
<id>urn:uuid:6d57252a-8bcf-f2f6-2475-77ae98afc0d3</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles4/about_thumb.jpg" alt="About: The Concept of the Global Hunger Index" /> <strong>The Global Hunger Index (GHI) is a tool designed to comprehensively measure and track hunger at global, regional, and national levels. GHI scores are calculated each year to assess progress and setbacks in combating hunger.</strong><br /> About &nbsp; The Concept of the Global Hunger Index &nbsp; &nbsp;&nbsp;&nbsp; About image Photo: Welthungerhilfe/Papa Shabani 2021; A smallholder farmer sells onions at a market in Luweero, Uganda. In many areas, disruptions to food systems triggered by the COVID-19 pandemic have undermined the livelihoods of small-scale farmers. Building resilient food systems requires not only raising agricultural productivity but also strengthening food transport, storage, and distribution. Hide ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles4/about_thumb.jpg" length="8346" type="image/jpeg"/>
</entry>
<entry>
<title>
<![CDATA[ Partner Spotlight: Welthungerhilfe In Sudan ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/case-studies/2021-sudan.html"/>
<id>urn:uuid:573688ed-7c4b-db7a-d575-8f71efa674f8</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles4/article355_thumb.png" alt="Partner Spotlight: Welthungerhilfe In Sudan" /> <strong>Welthungerhilfe, with its mandate to work on both humanitarian assistance and development cooperation, operates in many countries affected by violent conflict. One such country is Sudan.</strong><br /> Box 2.1 PARTNER SPOTLIGHT: WELTHUNGERHILFE IN SUDAN Welthungerhilfe, with its mandate to work on both humanitarian assistance and development cooperation, operates in many countries affected by violent conflict. One such country is Sudan, where decades of conflict, coupled with economic downturns, have led to widespread hunger. With a 2021 GHI score of 25.1, Sudan suffers from a serious level of hunger and ranks 95th out of 116 countries. A record 9.8 million people in Sudan—one-fifth of the population analyzed—faced high projected levels of acute food insecurity between June and September 2021 and require urgent assistance. North Darfur is forecast to be the worst-affected area (IPC 2021b). Operating in Sudan requires a clear understanding of the historical causes of conflict and its drivers, which are complex, politicized, and multi-level, encompassing local, national, regional, and international dimensions at the same time. The country has large numbers of both internally displaced persons (IDPs) and refugees from neighboring countries (IOM and WFP 2021; UNHCR 2021). Tensions over scarce livelihood assets and land have arisen between host communities and displaced persons as well as between pastoralists and farmers, particularly along migratory routes. Droughts, desertification, and floods are contributing to new conflicts in an environment where resources and opportunities are already under stress (OCHA 2020). It is now widely recognized that there can be no food and nutrition security without peace. To strengthen resilience and achieve food and nutrition security, Welthungerhilfe strives to take a systemic approach to food systems, including in conflict settings such as Sudan. It works along the humanitarian–development– peace-building nexus to provide relief and recovery in the event of acute shocks and stresses while strengthening resilience and livelihoods for host communities, IDPs, and refugees. Placing communities at the center of its work, Welthungerhilfe’s program also supports community-level peace-building initiatives. North Darfur is the region of focus for Welthungerhilfe’s operations in Sudan, along with the states of Gedaref, Kassala, and Red Sea. Welthungerhilfe addresses the most critical humanitarian needs of host communities, IDPs, and refugees through cash and voucher assistance, protection, shelter, nonfood items, and water, sanitation, and hygiene. It links those interventions with others aimed at improving human security, resilience, food and nutrition security, and livelihoods, as well as contributing to peace building and social cohesion. Activities include farmer and pastoralist field schools and training for women’s groups on food processing, home gardening, healthy nutrition, and income generation. A pilot intervention aimed at improving food and nutrition security and reducing competition over natural resources has led to the introduction of low-space vertical gardening for the production of fodder and vegetables in IDP camps in North Darfur. This program has improved access to nutritious food and created new income opportunities, even when land and water are in short supply, and thus represents a solution adapted to the existing context. Welthungerhilfe also helps promote peaceful dialogue, coexistence, and reconciliation in North Darfur through community- based resolution mechanisms (CBRMs), which bring together pastoral and farmer communities of diverse ethnicities along migratory routes. CBRMs target youth at risk of becoming engaged in violence, as well as women, whose participation is crucial for mitigating and resolving disputes within and between communities. CBRMs offer workshops on migratory route awareness, rehabilitation of migratory routes, and sensitization of communities. Welthungerhilfe’s project has linked CBRMs with relevant government ministries, legal institutions, the Sudan Humanitarian Aid Commission, and security services, giving rural communities better access to legal avenues of conflict resolution and resources. Nonetheless, the situation remains volatile, with flare-ups of political instability and violence in addition to natural disasters and the pandemic. As recent political developments have destabilized the official judicial system, CBRMs have become more important than ever. Welthungerhilfe seeks to increase the inclusion of youth, women, and marginalized communities in the CBRMs. ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles4/article355_thumb.png" length="14714" type="image/png"/>
</entry>
<entry>
<title>
<![CDATA[ Partner Spotlight: Concern Worldwide in Haiti ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/case-studies/2021-haiti.html"/>
<id>urn:uuid:125db747-50b4-56d2-26ca-806c56b0a7e4</id>
<updated>2021-10-13T23:01:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles4/Haiti_thumb.png" alt="Partner Spotlight: Concern Worldwide in Haiti" /> <strong>The resilience of the Haitian people in the face of environmental, social, economic, and political instability is as extraordinary as the scale of challenges they face daily.</strong><br /> Box 2.2 PARTNER SPOTLIGHT: CONCERN WORLDWIDE IN HAITI On Saturday, August 14, 2021, Haiti was hit by a 7.2-magnitude earthquake. At the time of writing, the scale of the disaster was unclear, but early estimates of 1,300 dead, 5,700 injured, and more than 15,000 homes destroyed or damaged were all expected to rise. The resilience of the Haitian people in the face of environmental, social, economic, and political instability is as extraordinary as the scale of challenges they face daily. Though not at war, the country has suffered violence over many decades. In 2004, a UN peacekeeping mission was deployed there when, for the first time in history, a mandate was given authorizing the use of force—not to address an active conflict or enforce a peace agreement, but because the political and humanitarian crisis was a threat to international peace and security. That UN mission continued until 2017 and was followed by a smaller peacekeeping mission. Having worked in Haiti for more than 27 years, Concern Worldwide has learned a number of lessons about how best to help people build resilience to the shocks and stresses they are confronted with. Its resilience-building work has been focused especially on Haiti’s urban centers, where the majority of Haitians live. Growing urbanization in Haiti has led to a high concentration of the population in the metropolitan area of Port-au-Prince, where sprawling slums and high unemployment put enormous pressure on the area’s limited social infrastructure and basic services. Since long before the catastrophic 2010 earthquake, Haitians have suffered from degraded living conditions, limited educational opportunities, and poor economic prospects. In recent months the country’s sociopolitical and economic context has deteriorated further (President Jovenel Moïse was assassinated on July 7), leaving marginalized communities even more vulnerable to social and natural shocks. One of the areas where Concern Worldwide works is Cité Soleil, a marginalized and stigmatized commune in the Port-au-Prince area with a population of more than 265,000. Throughout 2021, tensions in the commune have been high. Fuel scarcity, traffic disruptions, and the closure of businesses and schools have harmed the livelihoods of the poorest households. According to the National Coordination for Food Security (CNSA), 46 percent of the population—4.4 million Haitians—are food insecure and in need of urgent humanitarian action. In Cité Soleil, at the time of writing, 55 percent of households are in a food crisis or food emergency (CNSA 2021). Against this backdrop, where hunger and conflict collide, Concern Worldwide’s integrated programming consists of a range of interventions that work holistically. Its approach prioritizes working with and through local facilitators and community health workers, and it places a strong emphasis on its relationships with local institutions. Its collaboration with the professional school Haiti Tec and the training center Centre Animation Paysanne et d’Action Communautaire (CAPAC), for example, has encouraged these institutions to make additional investments in vulnerable communities. As part of its adaptive approach, Concern Worldwide seeks to use technology to best effect, including using mobile phones to distribute vouchers or delivering radio broadcasts about good health and nutrition practices. Concern Worldwide’s integrated urban program is designed to meet people’s basic needs while building their capacity to meet their future needs. It provides people with the means to buy food while ensuring that markets have high-quality products from preapproved local suppliers. The team helps promote good health and nutritional practices so people can achieve both food security and nutrition security, which are especially critical at this time. Despite the challenging context and growing needs, Concern Worldwide—working in collaboration with partners and local communities—has had a positive impact on families living in Cité Soleil. Its programming has helped improve the food security of 3,000 of the commune’s most vulnerable and food-insecure households. Its interventions have increased households’ access to food, reduced the number of families resorting to negative coping strategies, and improved people’s nutrition behavior, including their consumption of fruits and vegetables and their dietary diversity. Concern’s food security programming has contributed to a rise in the food consumption score in the commune. Since the onset of the organization’s food security programming in Cité Soleil, the share of the population with an acceptable food consumption score has risen from 39 percent to 73 percent, and the share of the target population reporting poor food consumption has fallen from 25 percent to just 2.1 percent. In the face of the myriad challenges faced by the people of Haiti, it is critical that these gains be protected and built on over the months and years to come. ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles4/Haiti_thumb.png" length="10414" type="image/png"/>
</entry>
<entry>
<title>
<![CDATA[ Albania ]]>
</title>
<link type="text/html" href="https://www.globalhungerindex.org/albania.html"/>
<id>urn:uuid:d33df7e6-7958-6d46-271c-ab70f7fb3a86</id>
<updated>2021-10-13T21:04:00+00:00</updated>
<summary type="html">
<![CDATA[ <img style="margin:5px; float:left;" src="https://www.globalhungerindex.org/media/images/articles3/Albania_thumb.png" alt="Albania" /> <strong>With a score of 6.2 in the 2021 Global Hunger Index, Albania has a level of hunger that is low.</strong><br /> In the 2021 Global Hunger Index, Albania ranks 25th&nbsp;out of the 116 countries with sufficient data to calculate 2021 GHI scores. With a score of 6.2, Albania has a level of hunger that is low. ≤ 9.9 low 10.0–19.9 moderate 20.0–34.9 serious 35.0–49.9 alarming ≥ 50.0 extremely alarming &nbsp; Trend for Albania's Indicator Values &nbsp; Note: Data for GHI scores, child stunting, and child wasting are from 1998–2002 (2000), 2004–2008 (2006), 2010–2014 (2012), and 2016–2020 (2021). Data for undernourishment are from 2000–2002 (2000), 2005–2007 (2006), 2011–2013 (2012), and 2018–2020 (2021). Data for child mortality are from 2000, 2006, 2012, and 2019 (2021). See Appendix B for the formula for calculating GHI scores and Appendix C for the sources from which the data are compiled. &nbsp; Download/Print this Page .modulecountry ]]>
</summary>
<author>
<name>Ethical Sector</name>
</author>
<link rel="enclosure" href="https://www.globalhungerindex.org/media/images/articles3/Albania_thumb.png" length="18873" type="image/png"/>
</entry>
</feed>
"""


class MockResponse:
    status_code = 200
    elapsed = timedelta(seconds=1)
    headers = {}
    url = "https://www.globalhungerindex.org/atom.xml"
    text = mock_feed_text


@pytest.mark.parametrize(
    "configuration,expected_record_keys",
    [
        (
            {
                "feed_urls": ["http://Ill-be-replaced-through-monkeypatch.com"],
                "feed_entry_replication_key": "updated",
            },
            [
                "feed_url",
                "feed_title",
                "entry_id",
                "entry_updated",
                "entry_title",
                "entry_link",
            ],
        ),
        (
            {
                "feed_urls": ["http://Ill-be-replaced-through-monkeypatch.com"],
                "feed_fields": ["title"],
                "feed_entry_fields": ["id", "title", "link"],
                "feed_entry_replication_key": "updated",
            },
            [
                "feed_url",
                "feed_title",
                "entry_id",
                "entry_updated",
                "entry_title",
                "entry_link",
            ],
        ),
        (
            {
                "feed_urls": ["http://Ill-be-replaced-through-monkeypatch.com"],
                "feed_fields": ["title"],
                "feed_entry_fields": ["title"],
                "feed_entry_replication_key": "updated",
            },
            [
                "feed_url",
                "feed_title",
                "entry_id",
                "entry_updated",
                "entry_title",
            ],
        ),
        (
            {
                "feed_urls": ["http://Ill-be-replaced-through-monkeypatch.com"],
                "feed_fields": ["title", "link"],
                "feed_entry_fields": ["title", "author"],
                "feed_entry_replication_key": "updated",
            },
            [
                "feed_url",
                "feed_title",
                "feed_link",
                "entry_id",
                "entry_updated",
                "entry_title",
                "entry_author",
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
    assert len(tap_records) == 10
    for record in tap_records:
        print(record)
        assert record["type"] == "RECORD"
        assert record["stream"] == "feed"
        assert record["record"]["feed_url"] == MockResponse.url
        assert list(record["record"].keys()) == expected_record_keys


def get_parsed_records(tap_output: str) -> List[dict]:
    """Generates a list of the records from the stdout string provided"""
    return [
        json.loads(_ + "}") for _ in tap_output.split("}\n") if '"type": "RECORD' in _
    ]
