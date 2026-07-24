// ─── Types ────────────────────────────────────────────────────────────────────

export interface AboutStat {
  value: string;
  label: string;
}

export interface AboutValue {
  icon:        string;
  title:       string;
  description: string;
}

export interface AboutTimelineItem {
  year:        string;
  title:       string;
  description: string;
}

export interface AboutMission {
  title:      string;
  paragraphs: string[];
  question:   string;
  closing:    string;
}

export interface AboutGalleryItem {
  image: string;
  alt:   string;
}

export interface AboutSocialLink {
  icon:  string;
  label: string;
  href:  string;
}

export interface AboutData {
  name:     string;
  tagline:  string;
  logo:     string;
  intro:    string[];
  mission:  AboutMission;
  stats:    AboutStat[];
  values:   AboutValue[];
  timeline: AboutTimelineItem[];
  gallery:  AboutGalleryItem[];
  socials:  AboutSocialLink[];
}

// ─── Default Data ─────────────────────────────────────────────────────────────
// Real backstory (anonymised), sourced from "Vision Mission - Draft.docx",
// "About Us Page (Heartland Feel)" — company names generalised per request.

export const defaultAboutData: AboutData = {
  name:    'TheEnoughPoint.com',
  tagline: 'Two Bishan boys, 18 years of work, and the long road to semi-retirement.',
  logo:    '/img/brand/logo-icon-96.png',

  intro: [
    'We are two childhood friends from Bishan. Long before we understood money, investing, careers, business, CPF, or the idea of financial freedom, we were just two boys growing up in HDB flats, hanging around Bishan MRT station, looking over the shoulders of older kids playing Magic: The Gathering.',
    'We were curious. We were ordinary. We were not born rich. There was no inheritance waiting for us, no scholarship path carefully laid out, no family fortune, no jackpot. Just school, work, choices, mistakes, recovery, and the slow compounding of decisions made over many years.',
    "We both did well enough in school to make it into good universities. But even though our starting points were similar, our paths eventually split. FI went into finance — the institutional side, managing money professionally at a major insurer for the better part of two decades. Markets, portfolios, the long arithmetic of retirement: he's the numbers half of this pair.",
    'RE went a very different way — engineering, then years in sales at a global solutions infrastructure provider, and eventually building his own business, which was later acquired. Since 2019 he has had the privilege of working largely on his own time.',
    'Neither of our journeys was glamorous. They were not straight lines. They were full of wrong turns, bruised egos, career doubts, financial lessons, family responsibilities, business risks, and moments where we wondered whether we were truly making the right choices. But looking back, a few decisions mattered: choosing to learn, choosing to work hard when it counted, choosing not to inflate our lifestyles too quickly, choosing to invest, choosing to build options before we desperately needed them.',
    'This website was born from those conversations. Every Thursday at 10am, we play pickleball. Somewhere between rallies, missed shots, and aching knees, we found ourselves talking about the past 18 years of working life — the wins, the traps, the lucky breaks, the painful lessons, and the quiet choices that gave us a head start. We realised there were stories worth telling — not because we have figured everything out, but because many Singaporeans in their 30s and 40s are asking the same questions we once asked, and still ask today.',
  ],

  mission: {
    title: "It's Your Journey, Your Enough Point",
    paragraphs: [
      "At its core, TheEnoughPoint is about sharing our stories. We're both 43 today, and if we're honest — we're still on our own journey toward financial independence. We haven't 'arrived' in the way finance content likes to imply arrival looks. What we have done is reach our own enough point: the place where we can slow things down a little, stop chasing more for the sake of more, and actually appreciate life for what it is.",
      "How we intend to keep it that way is a lot of what we write about here — the actual numbers behind our own enough point, the trade-offs that got us there, and the ongoing work of not letting lifestyle quietly creep back up and undo it.",
    ],
    question: 'But everybody wants different things, and everybody has different aims — so we have to ask you the same question we keep asking ourselves: what is your enough point?',
    closing: "Because the answer is different for everyone, this site isn't just our numbers and our concepts. We make it a point to design and build custom calculators, so you can visualise your own journey and your own enough point — wherever your starting point may be. It is your journey. It is your enough point.",
  },

  stats: [
    { value: '18',       label: 'Years of Work Between Us' },
    { value: '2',        label: 'Bishan Kids' },
    { value: 'Thu 10am', label: 'Pickleball, Where It Started' },
    { value: '4',        label: 'Pillars We Write About' },
  ],

  values: [
    {
      icon:        'bi:shield-check',
      title:       'No Hype, No Shortcuts',
      description: 'No get-rich-quick language, no target prices, no model portfolios pretending to be advice. Just what actually worked, what did not, and why.',
    },
    {
      icon:        'bi:eye',
      title:       'Honest About the Losses Too',
      description: 'Our journeys were full of wrong turns and bruised egos. We write about those as openly as the wins — this is a warning sign as much as a roadmap.',
    },
    {
      icon:        'bi:globe-americas',
      title:       'Singapore-Specific',
      description: 'CPF, SRS, HDB, T-bills — the real mechanics of building enough here, not generic personal finance advice imported from elsewhere.',
    },
    {
      icon:        'bi:lightning-charge',
      title:       'Two Perspectives, One Goal',
      description: 'FI brings two decades of institutional finance. RE brings sales, engineering, and a business built and sold. Between us, the fuller picture.',
    },
    {
      icon:        'bi:chat-quote',
      title:       'Educational, Not Advice',
      description: 'Views are personal and educational only — not a recommendation to buy, sell, or hold anything, and not a substitute for your own judgement.',
    },
    {
      icon:        'bi:people',
      title:       'Written for the Ordinary Reader',
      description: 'We were not born into wealth. We write for people who were not either, and still want more freedom, more choices, and a head start.',
    },
  ],

  timeline: [
    {
      year:        'Childhood',
      title:       'Two Boys From Bishan',
      description: 'HDB flats, loitering at Bishan MRT, watching the older kids play Magic: The Gathering and pretending we understood the rules. Curious, ordinary, definitely not born rich.',
    },
    {
      year:        'University',
      title:       'Same Start, Different Bus Routes',
      description: "We both scraped into decent universities. That's about where the similarities end — one of us fell into spreadsheets and financial models, the other somehow ended up in engineering, then sales, still not entirely sure how that happened.",
    },
    {
      year:        '~18 Years',
      title:       'The Long, Unglamorous Middle',
      description: 'Nearly two decades of ordinary, occasionally soul-crushing work — one of us moving other people\'s money around at a big insurer, the other selling infrastructure kit by day and building something of his own on the side. No overnight anything. Just showing up, a lot.',
    },
    {
      year:        '2019',
      title:       'The Business Finally Sells',
      description: "After years of nights and weekends, RE's business gets acquired. Turns out freedom looks a lot like a four-day work week and being home by 4.30 — not a yacht.",
    },
    {
      year:        'Ongoing',
      title:       'Thursday, 10am, Pickleball',
      description: 'A standing pickleball date that somehow turned into two decades of financial and business war stories — usually somewhere between missed shots and complaints about our knees.',
    },
    {
      year:        '2026',
      title:       'TheEnoughPoint Is Born',
      description: 'All those Thursday conversations finally spill out into a website. Part roadmap, part product review, part business diary, part cautionary tale, part folktale — and yes, still very much a work in progress.',
    },
  ],

  // No authentic photography yet — left empty rather than using unrelated stock
  // images. AboutGallery is not rendered on the page until this is populated.
  gallery: [],

  socials: [
    { icon: 'bi:twitter-x', label: 'X',        href: '#' },
    { icon: 'bi:telegram',  label: 'Telegram',  href: '#' },
  ],
};
