"""Corpus data definitions and generator helpers for Glastonbury Festival 2025."""
import json
from pathlib import Path
from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
LEGAL_DIR = ROOT / "data" / "landing" / "legal"
NEWS_DIR = ROOT / "data" / "landing" / "news"


class SafePDF(FPDF):
    """FPDF subclass that handles standard latin-1 text safely."""
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def write_heading(self, text: str, size: int = 14) -> None:
        self.set_font("Helvetica", style="B", size=size)
        safe_text = text.encode("latin-1", "replace").decode("latin-1")
        self.multi_cell(0, 8, safe_text)
        self.ln(2)

    def write_body(self, text: str, size: int = 10) -> None:
        self.set_font("Helvetica", size=size)
        safe_text = text.encode("latin-1", "replace").decode("latin-1")
        self.multi_cell(0, 6, safe_text)
        self.ln(2)


def generate_pdf_1() -> Path:
    """Generate Glastonbury Access Information 2025 PDF."""
    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    pdf = SafePDF()
    pdf.add_page()
    pdf.write_heading("ACCESS INFORMATION 2025", size=16)
    pdf.write_body(
        "The 2025 Glastonbury Festival will take place from Wednesday 25th - Sunday 29th June.\n"
        "Glastonbury Festival is committed to being an event accessible to all which is why we have "
        "been working with Attitude is Everything since 2005 to ensure we can achieve this.\n"
        "Attitude is Everything is a charity set up to help improve D/deaf and disabled people's access to "
        "live music. Glastonbury Festival is currently signed up to their 'Live Events Access Charter'.\n"
        "For information on how to buy tickets, plus the access facilities available to festival goers please "
        "read the following sections.\n"
        "If you have any further questions, please email the festival's Access Team - accessibility@glastonburyfestivals.co.uk\n"
        "Please be aware that the Access Team is currently working part time, so at busy periods please "
        "allow up to 7 days for us to respond to your enquiry."
    )

    sections = [
        ("1. Ticket Information",
         "There are no separate weekend tickets for festival goers with access requirements. Anyone "
         "wanting to attend the festival must register and book tickets in one of the upcoming ticket sales.\n"
         "General Admission full weekend tickets (valid from Wednesday 25th June to Sunday 29th June) "
         "for Glastonbury 2025 cost GBP 373.50 + a GBP 5 booking fee.\n"
         "Combined Coach Tickets - Ticket + coach travel options went on sale at 6pm (GMT) on Thursday 14th November 2024.\n"
         "General admission tickets - Tickets went on sale at 9am (GMT) on Sunday 17th November 2024.\n"
         "Tickets for the Festival are sold exclusively at glastonbury.seetickets.com.\n"
         "You could book up to 6 tickets per transaction by paying a deposit of GBP 75 per person when tickets went on sale. "
         "The remaining balance will then be payable in the first week of April 2025 (from 09:00 BST Tuesday 1st April - 23:59 BST Monday 7th April).\n"
         "Ticket Resale: There will be a resale of cancelled Festival tickets in the spring. Registration is free of charge and compulsory for everyone aged 13 or over."),

        ("2. Registering for the Access Facilities",
         "All Festival-goers (including children 12 years and under) needing to use any of the access facilities, "
         "including the PA ticket scheme, must complete the Festival's online access application form, and have either a valid "
         "Nimbus Access Card or the digital Nimbus Glastonbury Access Pass.\n"
         "The deadline for Access Applications for Glastonbury 2025 is the 30th April.\n"
         "When you have paid your ticket deposit, email the Access Team to request the link to the online application form."),

        ("3. Personal Assistant / PA Ticket Scheme",
         "Festival goers unable to attend the Festival without the support of a Personal Assistant (PA) can apply to use the "
         "PA Ticket Scheme, which includes a complimentary ticket for your PA at no extra cost.\n"
         "Festival goers must have the +1 requirement on their Access Card or digital Glastonbury Access Pass. The scheme is not run first-come first-served.\n"
         "You must pay the ticket deposit on your own ticket before completing the form. The closing date is 30th April.\n"
         "Terms: PAs must arrive and leave with the customer, be over 18, and be able to assist in emergencies. Children under 13 cannot claim PA tickets."),

        ("4. Accessible Campsite",
         "The Accessible Campsite is in Spring Ground which is on the west side of the Festival site next to Woodsies Tent. "
         "It is stewarded 24/7. Facilities include:\n"
         "- Wheelchair accessible and standard unisex toilets\n"
         "- Wheelchair adapted showers (strictly for access customers with wristbands, not PAs)\n"
         "- Charging facilities for wheelchairs and medical equipment\n"
         "- Changing Places unit featuring a changing bed, toilet, sink and hoist (bring your own slings)\n"
         "- Accessible sinks and freshwater points, fridge for secure medication storage, hot water for cooking/drinks\n"
         "- Campsite Hub with support desk and free daily treatments (massage, reflexology, reiki)\n"
         "Group & Tent Size: Maximum of 3 other people (total 4 people) staying with an access customer. Maximum of 2 tents per group of 4. "
         "Gazebos are strictly not allowed and will be removed."),

        ("5. Campervan & Caravan Spaces",
         "Wicket Ground: Located next to Spring Ground, reserved for festival-goers unable to camp due to disability. "
         "Wheelchair-accessible toilets and charging facilities are available. Only campervans under 8m long.\n"
         "East Campervan Field: Reserved accessible area. Tickets go on sale 28th November at 12 noon.\n"
         "Bath & West Showground: Accommodates vehicles under and over 8m. No charging facilities available."),

        ("6. Viewing Platforms / Viewing Areas",
         "Raised viewing platforms are located at all main stages, solely for festival-goers who need to be seated plus one accompanying person.\n"
         "Customers must apply for a Viewing Platform (VP) pass. Run on a first-come first-served basis; when full, stewards revert to one-off/one-on.\n"
         "Chairs are not provided on platforms; customers and 1 companion may bring their own folding chairs.\n"
         "Wheelchair charging points, accessible and standard toilets are available at all viewing platforms. Smoking is strictly prohibited."),

        ("7. Accessible Toilets",
         "Locked wheelchair accessible and standard toilets throughout the festival site, accessible only to registered access customers "
         "(e.g., customers with IBS or IBD). Applications must be submitted by 30th April.\n"
         "Toilets are non-flushing but provide hand sanitizer. A Changing Places unit with electric hoist is in the Accessible Campsite."),

        ("8. Festival Short Cuts",
         "Short cut routes exist across busy working areas to reduce walking distances for festival-goers with mobility issues/wheelchair users. "
         "Available to access customer plus 1 companion. They do not offer easier access to toilets and are busy working zones."),

        ("9. Deaf Customers",
         "BSL Provision: Free British Sign Language (BSL) interpreters at stages and spoken word venues. Advance booking available.\n"
         "Induction/Hearing Loops: Installed at Cabaret Tent, Astrolabe, Big Top Circus Tent, Cinema Tent, Leftfield Tent, and Accessible Campsite HQ."),

        ("10. Blind and Visually Impaired Customers",
         "A team of trained sighted guides is available during the Festival to aid blind and visually impaired festival goers."),

        ("11. Wheelchair Hire",
         "Electric and manual wheelchairs are available to hire in advance via the Access Application Pack. Wheelchair charging is available across site locations."),

        ("12. Sensory Calm Spaces",
         "Sensory Calm Tents in various locations provide low-level stimulation and recalibration zones for neurodivergent festival-goers, "
         "managed by autism specialists. Weighted blankets and ear defenders are provided. Samaritans offer 24-hour emotional support from Green Fields."),

        ("13. Assistance Dogs and Guide Dogs",
         "Accredited assistance dogs trained by IGDF or ADI members are welcomed. Must have the Assistance Dog symbol on Access Card.\n"
         "Owners must camp in the accessible campsite or accessible campervan field and are responsible for hygiene and clearing waste."),

        ("14. Travel and Arrival",
         "Accessible Car Park: Located via Yellow Gate on west of site. Only for access customers with pre-booked access parking tickets.\n"
         "Wheelchair Accessible Shuttle Bus: Runs between accessible car park, accessible campsite, and drop-off points around site (customer + 1 companion).\n"
         "Coach Arrival: Shuttle bus transports access customers from Coach Station (Pedestrian Gate A) to Access Arrivals Tent.\n"
         "Worthy View & Sticklinch: Worthy Shuttle runs to Worthy View. No bus runs to Sticklinch; must walk via Gate A."),

        ("15. Crew, Performers and Volunteers Accessibility",
         "Staff and performers needing access provisions must apply via crew.accessibility@glastonburyfestivals.co.uk."),

        ("16. Site Layout & Ground Conditions",
         "1500 acres of farmland in Somerset. Uneven grassy terrain, hills, stone/gravel paths, temporary trakways. Muddy when wet, dusty when dry.\n"
         "Distances from Accessible Campsite: Bus Station 700m, Pyramid Stage VP1 900m, Other Stage 1km, The Park 1.8km, Late Night Area 2km."),

        ("17. Temporary Impairments",
         "Access facilities are NOT available for temporary impairments such as broken bones, healing wounds, or pregnancy. "
         "The Festival cannot offer reserved parking or buggy assistance for temporary conditions; please refer to Medical and First Aid.")
    ]

    for title, body in sections:
        pdf.write_heading(title, size=12)
        pdf.write_body(body, size=10)

    out_path = LEGAL_DIR / "access_information_2025.pdf"
    pdf.output(str(out_path))
    return out_path


def generate_pdf_2() -> Path:
    """Generate Official Pre-Erected Campsites Accommodation Terms PDF."""
    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    pdf = SafePDF()
    pdf.add_page()
    pdf.write_heading("GLASTONBURY FESTIVAL 2025", size=16)
    pdf.write_heading("OFFICIAL PRE-ERECTED CAMPSITES ACCOMMODATION BOOKING TERMS & CONDITIONS", size=13)
    pdf.write_body(
        "In making an accommodation booking for the Glastonbury Festival official pre-erected campsites (Official Campsite(s)), "
        "you are agreeing to the code of conduct laid out by Glastonbury Festival Events Ltd (GFEL) and the below terms.\n"
        "These terms provide that accommodation may not be used in connection with any Commercial Activity on or off site. "
        "All Commercial Activity must be separately agreed with Festival management and will be subject to a fee."
    )

    terms = [
        "1. All persons aged 13 or over occupying accommodation must have valid full weekend Festival tickets.",
        "2. Names of all residents must be supplied when booking, final confirmation due one week prior. Wristbands issued on ticket presentation.",
        "3. Bookings are non-transferable. Cancellations before 23:59 May 9th 2025 incur GBP 25 admin charge per unit. No refunds after this date.",
        "4. The Premises Licence Holder (PLH) and GFEL reserve the right to refuse admission, evict persons committing criminal offences, disorderly/anti-social behaviour, or possessing contraband/prohibited articles.",
        "5. Admission is at ticketholder's own risk. GFEL and PLH are not liable for loss, injury or damage unless caused by gross negligence.",
        "6. Duplicate tickets will not be issued for lost or stolen tickets.",
        "7. Accommodation bookings are only valid when booked directly with official agents (See Tickets). Tickets cannot be resold, transferred or used in promotions/competitions.",
        "8. Breaches of clauses 7 or 11 result in immediate cancellation without refund and eviction from the Festival.",
        "9. Strictly no commercial trading, unauthorised photography/filming or commercial activity allowed without written consent.",
        "10. Photography and filming: Professional recording equipment without consent is prohibited. Personal cameras and mobile phones permitted for private use only.",
        "11. Commercial Activity includes ambush marketing, sponsored social posts, brand influencing. Hashtags like #ad, #gifted, #prinvite, #thanksto(partner) are strictly prohibited.",
        "12. Tickets and accommodation cannot be used as prizes, competitions, or promotional campaigns.",
        "13. GFEL owns registered trademarks for Glastonbury, Glasto, Worthy Farm, Pyramid Stage, Ribbon Tower. Unauthorised use is prohibited.",
        "14. GFEL reserves rights to seek takedowns, damages, and retrospective fees for unauthorised commercial activities.",
        "15. Ticket holders consent to being filmed, photographed and recorded for broadcast, security, and archive purposes.",
        "16. Wristbands removed or tampered with will be rendered invalid and will not be replaced. Tickets and wristbands remain property of GFEL until 5pm Monday 30th June 2025.",
        "17. Lead bookers accept liability for loss or damage to structures beyond general wear and tear.",
        "18. Persons under 16 must be accompanied by a responsible adult aged 18+ at all times. Persons aged 13-15 may exit/re-enter with Parental Permission wristband.",
        "19. Compliance with all HM Government legislation and public health guidelines is mandatory."
    ]
    for term in terms:
        pdf.write_body(term)

    pdf.write_heading("2025 INFORMATION & NOTIFICATIONS", size=13)
    notifs = [
        "1. Pitches are allocated on a first-come, first-served basis.",
        "2. Only pre-erected facilities provided by the Festival are permitted. Unauthorised tents or gazebos will be dismantled and confiscated.",
        "3. All cars require a separate car parking ticket specific to the designated campsite, purchased in advance.",
        "4. Campervans and caravans are not permitted in official pre-erected campsites; designated campervan fields require separate tickets.",
        "5. No vehicles parked or tents pitched in fire lanes at any time.",
        "6. No unauthorised sound systems or trading permitted. Buy only official merchandise.",
        "7. Prohibited items: Fireworks, Chinese lanterns, drones, flares, burning plastics, generators, glass containers, weapons, laser pens.",
        "8. Security searches apply to all tents and vehicles. Confiscated illegal items will not be returned.",
        "9. No animals allowed onsite with the exception of registered guide and assistance dogs.",
        "10. All litter must be cleared into bins or recycling points.",
        "11. Open fires prohibited; small barbecues allowed at a safe distance from tents. Communal campfires are supervised.",
        "12. Toilets and urinals must be used; do not pollute streams and hedges.",
        "13. Chairs, buggies, trolleys must not obstruct busy areas or stage fronts.",
        "14. Medical treatment provided by Festival Medical Services (separate legal entity).",
        "15. Worthy View access involves a steep gradient not recommended for wheelchair users or prams.",
        "16. Smoking, vaping, and e-cigarettes are banned in all enclosed public areas and tented accommodation.",
        "17. Carbon Monoxide safety: Never take a lit or smouldering BBQ or gas camping stove into a tent or unit.",
        "18. Challenge 21 policy for alcohol: Anyone looking under 21 must show ID or wear Challenge 21 wristband.",
        "19. Late-night areas and front-of-stage barriers may be unsuitable for children.",
        "20. All tents must be vacated by 5pm on Monday 30th June 2025.",
        "21. Performances may use strobe lighting, lasers, and pyrotechnics.",
        "22. Warning: Excessive exposure to loud music may cause damage to hearing."
    ]
    for notif in notifs:
        pdf.write_body(notif)

    out_path = LEGAL_DIR / "campsite_terms_and_conditions_2025.pdf"
    pdf.output(str(out_path))
    return out_path


def generate_pdf_3() -> Path:
    """Generate Sunday Ticket Terms & Conditions PDF."""
    LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    pdf = SafePDF()
    pdf.add_page()
    pdf.write_heading("GLASTONBURY FESTIVAL EVENTS LTD", size=16)
    pdf.write_heading("SUNDAY TICKET TERMS & CONDITIONS OF ENTRY 2025", size=13)
    pdf.write_body(
        "Terms and conditions for holders of Sunday Tickets for Glastonbury Festival 2025 (hereafter 'the Festival')."
    )

    clauses = [
        "1. Sunday Tickets for Glastonbury Festival 2025 are non-refundable after 9th May 2025 and always non-transferable. Cancellations before 23:59 on 9th May 2025 will be reimbursed less the GBP 25 administration fee. Booking fees and postage charges are non-refundable.",
        "2. Sunday Tickets are only valid for entry from 08:00 on Sunday 29th June 2025.",
        "3. Artist and performer line-up and all billed attractions are subject to change at any time without notice. Access to any performance may be restricted for safety.",
        "4. Premises Licence Holder (PLH) and GFEL reserve rights to refuse admission or evict persons for breach of entry terms, anti-social behaviour, or public nuisance.",
        "5. Admission is at ticketholder's own risk. GFEL and PLH are not liable for losses, injuries, or vehicle damages unless caused by negligence.",
        "6. Duplicate tickets will not be issued for lost or stolen tickets.",
        "7. Tickets are only valid when purchased from official agents (See Tickets). Tickets purchased from unauthorised sources will be refused admission.",
        "8. Tickets are personalised to the named ticket holder with photo ID. Resale or transfer is strictly prohibited.",
        "9. Breached tickets will be confiscated immediately without refund.",
        "10. Commercial photography, filming, or broadcasting equipment is banned without written permission. Mobile devices for private personal use are permitted.",
        "11. Tickets cannot be used in competitions, promotions, marketing campaigns, or advertising without written permission.",
        "12. Commercial activity definition includes ambush marketing, sponsored social posts, and influencer tags (#ad, #gifted).",
        "13. Festival trademarks (Glastonbury, Glasto, Pyramid Stage) are protected intellectual property.",
        "14. GFEL reserves rights to confiscate tickets and seek damages for unauthorised commercial use.",
        "15. Ticket holders consent to being filmed and recorded for broadcast and security purposes.",
        "16. Wristbands remain property of GFEL until 5pm Monday 30th June 2025. Tampered or lost wristbands will not be replaced.",
        "17. Children under 16 must be accompanied by an adult aged 18+ at all times.",
        "18. Compliance with all statutory legislation and public health guidance is required."
    ]
    for clause in clauses:
        pdf.write_body(clause)

    pdf.write_heading("2025 INFORMATION & NOTIFICATIONS", size=13)
    rules = [
        "1. Essential packing and safety information can be found on glastonburyfestivals.co.uk.",
        "2. Cars require a separate Sunday parking ticket.",
        "3. Do not buy tickets from street traders or unauthorised agencies; beware of forged tickets.",
        "4. GFEL accepts no responsibility for goods or services purchased from third parties.",
        "5. Official merchandise is sold onsite; avoid street traders.",
        "6. Use only provided toilets and urinals. Do not pollute farmland, streams or hedges.",
        "7. Use litterbins and recycling points provided across the farm.",
        "8. Security search: Vehicles and bags are liable to search on entry. Refusal to comply results in eviction.",
        "9. Prohibited items: Fireworks, Chinese lanterns, drones, flares, burning plastics, glass, generators, weapons, laser pens.",
        "10. No animals allowed onsite, with the exception of registered guide and assistance dogs.",
        "11. Challenge 21 policy operates at all bars: Proof of age required for anyone appearing under 21.",
        "12. Front-of-stage barriers and late-night areas may be restricted or unsuitable for children.",
        "13. Warning: Excessive exposure to loud music may cause damage to your hearing."
    ]
    for rule in rules:
        pdf.write_body(rule)

    out_path = LEGAL_DIR / "sunday_ticket_terms_and_conditions_2025.pdf"
    pdf.output(str(out_path))
    return out_path


def get_news_articles() -> list[dict]:
    """Return the curated list of 5 news articles."""
    art1 = {
        "url": "https://www.glastonburyfestivals.co.uk/news/2025-ticket-sale-faq/",
        "title": "2025 Ticket Sale FAQ",
        "date_crawled": "2024-11-05T11:55:16+00:00",
        "content_markdown": (
            "# 2025 Ticket Sale FAQ\n\n"
            "**Published:** 5th November 2024 | **Source:** Glastonbury Festivals News\n\n"
            "Please find below answers to Frequently Asked Questions about booking tickets for Glastonbury Festival 2025.\n\n"
            "### Ticket Sale Dates & Pricing\n"
            "- **Ticket + Coach Packages:** On sale at 6pm GMT on Thursday, 14th November 2024.\n"
            "- **General Admission Tickets:** On sale at 9am GMT on Sunday, 17th November 2024.\n"
            "- **Price:** General admission full weekend tickets cost £373.50 + £5 booking fee per person.\n"
            "- **Deposit:** A £75 deposit per ticket is paid during the November sale. The remaining balance is payable from 1st to 7th April 2025.\n"
            "- **Resale:** Cancelled and returned tickets will be released in the Spring 2025 resale.\n\n"
            "### Mandatory Registration\n"
            "- Everyone aged 13 or older must be registered with a valid photo before booking.\n"
            "- Registration is free of charge on glastonbury.seetickets.com.\n"
            "- Up to 6 tickets can be booked per transaction in the general admission sale."
        )
    }

    art2 = {
        "url": "https://www.glastonburyfestivals.co.uk/news/the-full-glastonbury-2025-line-up-is-here-with-set-times/",
        "title": "The full Glastonbury 2025 line-up is here - with set times",
        "date_crawled": "2025-06-03T10:00:00+00:00",
        "content_markdown": (
            "# The full Glastonbury 2025 line-up is here - with set times\n\n"
            "**Published:** 3rd June 2025 | **Source:** Glastonbury Festivals News\n\n"
            "The complete line-up for Glastonbury Festival 2025, taking place 25th-29th June, has been unveiled across all major stages.\n\n"
            "### Major Stages Highlights\n"
            "- **Pyramid Stage:** World-renowned headliners and afternoon legends slot.\n"
            "- **Other Stage:** Alternative and indie rock acts playing from morning until late night.\n"
            "- **West Holts:** Soul, funk, jazz, and global sounds with spectacular evening light shows.\n"
            "- **Woodsies & The Park:** Emerging talent, indie darlings, and secret unannounced sets.\n"
            "- **Late Night Areas:** Silver Hayes, Block9, Shangri-La, and The Common opening from dusk until dawn."
        )
    }

    art3 = {
        "url": "https://www.glastonburyfestivals.co.uk/news/think-before-you-pack-for-this-years-festival-25/",
        "title": "Think before you pack for this year's Festival!",
        "date_crawled": "2025-06-11T10:12:16+00:00",
        "content_markdown": (
            "# Think before you pack for this year's Festival!\n\n"
            "**Published:** 11th June 2025 | **Source:** Glastonbury Festivals Official Advice\n\n"
            "In just two weeks, gates finally open for Glastonbury 2025! When preparing your journey to Worthy Farm, "
            "please bear in mind our core ethos: **Love Worthy Farm, Leave No Trace**. Only bring what you can carry, and crucially, what you can take home with you.\n\n"
            "### Essential Packing List (What to Bring)\n"
            "- **Documents & Tickets:** Your festival ticket, valid photo ID (passport or driving licence), travel/coach tickets, parking pass if driving.\n"
            "- **Camping Gear:** A sturdy, reusable tent (with spare pegs), sleeping bag, roll mat or airbed, and a mallet. Commit to taking your tent home.\n"
            "- **Footwear & Clothing:** Wellies or sturdy walking boots are essential for the uneven farm terrain. Pack waterproof jackets, warm layers for chilly nights, and sunhats for hot days.\n"
            "- **Health & Hygiene:** Reusable water bottle (refillable free at 800+ taps on site), toilet roll, hand sanitiser, prescribed medication, biodegradable toiletries, suncream, earplugs for sleep.\n"
            "- **Money & Tech:** Portable power bank, head torch with spare batteries, contactless cards and an emergency stash of cash.\n"
            "- **Bag Identification:** Clearly label all luggage with your name and mobile phone number.\n\n"
            "### Strictly Prohibited Items (What NOT to Bring)\n"
            "- **Glass of any kind:** Completely banned. Perfume bottles, mirrors, spirit bottles, and food jars will be confiscated at gates and not returned.\n"
            "- **Weapons & Dangerous Items:** Knives, fireworks, flares, pyrotechnics, sky lanterns, laser pens.\n"
            "- **Illegal Substances:** Nitrous oxide (laughing gas), illegal drugs, and psychoactive substances are banned.\n"
            "- **Environmental Hazards:** Disposable vapes are banned due to fire risk and battery pollution. Body glitter (even biodegradable) is prohibited because it cannot break down in soil without industrial heat.\n"
            "- **Bulky Gear:** Gazebos take up crucial tent space and will be confiscated. Generators, sound systems, and kites are strictly forbidden.\n"
            "- **Animals:** Strictly no animals onsite with the exception of registered guide and assistance dogs."
        )
    }

    art4 = {
        "url": "https://www.glastonburyfestivals.co.uk/news/plan-your-journey-travel-sustainably/",
        "title": "Plan your journey - travel sustainably",
        "date_crawled": "2025-06-06T15:14:27+00:00",
        "content_markdown": (
            "# Plan your journey - travel sustainably\n\n"
            "**Published:** 6th June 2025 | **Source:** Glastonbury Festivals Travel Guide\n\n"
            "With just 19 days until Glastonbury 2025 gates open, festival-goers are encouraged to plan travel with sustainability at the forefront. "
            "Over a third of all ticket-holders travel by public transport or bicycle, significantly cutting the festival's carbon footprint.\n\n"
            "### Green Travel Options\n"
            "- **Train Travel:** Trains produce 67% fewer carbon emissions than driving. Castle Cary station is the primary rail gateway. A free, regular shuttle bus service operates between Castle Cary station and the Festival bus station for all ticket-holders.\n"
            "- **Cycling (Bike to Glasto):** Cycling is the greenest way to arrive. Free secure bike lock-ups are provided, alongside a dedicated cyclists-only campsite featuring hot showers. Route maps and cycling corridors are curated with Sustrans.\n"
            "- **Coach Services:** National Express operates direct coach routes from over 90 pickup points across the UK directly into the Festival Bus Station inside Pedestrian Gate A.\n"
            "- **Local Buses:** Frequent bus connections run from Bristol Temple Meads, Bath, Wells, and Shepton Mallet to the festival site.\n"
            "- **Car Sharing:** For those who must drive, organizers urge drivers to fill every vehicle seat. Use lift-sharing platforms to reduce road congestion and emissions.\n"
            "- **Carbon Calculator:** Glastonbury provides an online Travel Carbon Calculator built by Onboard.Earth to help attendees track their trip impact."
        )
    }

    art5 = {
        "url": "https://www.glastonburyfestivals.co.uk/news/download-our-2025-app-keep-your-phone-charged/",
        "title": "Download our 2025 App + keep your phone charged",
        "date_crawled": "2025-06-17T09:30:00+00:00",
        "content_markdown": (
            "# Download our 2025 App + keep your phone charged\n\n"
            "**Published:** 17th June 2025 | **Source:** Glastonbury Festivals Technology News\n\n"
            "The official Glastonbury 2025 mobile application, powered by Vodafone, is now available for download on iOS and Android. "
            "The app is designed to help festival-goers navigate the 1,500-acre site and plan their ultimate weekend.\n\n"
            "### Key App Features\n"
            "- **Personal Line-up Planner:** Bookmark favourite artists, preview stage times, and receive notifications before performances start.\n"
            "- **Interactive GPS Map:** Search stages, food traders, medical tents, water points, and pinpoint your tent or meeting spots.\n"
            "- **Live Location Sharing:** Safely share location with your festival group and sync schedule favorites with friends.\n"
            "- **Worthy FM & Spotify:** Stream live Worthy FM radio and listen to stage-curated Spotify playlists.\n"
            "- **My Highlights:** Track step counts and receive a personalised recap of stages and artists visited over the weekend.\n\n"
            "### Vodafone Connect & Charge Tent\n"
            "Located opposite the Leftfield area, the Vodafone Connect & Charge tent provides vital power and network services:\n"
            "- **Free Mobile Charging:** Open to all festival-goers regardless of which mobile network provider they use.\n"
            "- **Battery Pack Rental:** Attendees can rent a portable battery pack on-site and exchange it once a day for a fully charged replacement for free. Deposits are refunded upon return at the end of the festival.\n"
            "- **Free eSIM Trials:** Visitors can activate a free 7-day 5G data eSIM trial via in-app links or QR codes at the Vodafone tent.\n"
            "- **Enhanced 5G Capacity:** Vodafone deployed 10 mobile masts across Worthy Farm to deliver high-speed 5G connectivity."
        )
    }

    return [art1, art2, art3, art4, art5]
