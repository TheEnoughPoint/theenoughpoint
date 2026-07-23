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
  stats:    AboutStat[];
  values:   AboutValue[];
  timeline: AboutTimelineItem[];
  gallery:  AboutGalleryItem[];
  socials:  AboutSocialLink[];
}

// ─── Default Data ─────────────────────────────────────────────────────────────

export const defaultAboutData: AboutData = {
  name:    'Portal News',
  tagline: 'Independent Journalism. Global Perspective.',
  logo:    '/img/logo.png',

  intro: [
    'Portal News was founded in 2019 with a simple mission: deliver accurate, balanced, and timely news from every corner of the world. What began as a small team of five reporters has grown into a newsroom trusted by millions of readers across the globe.',
    'We believe journalism exists to serve the public, not any single interest. Every story we publish is fact-checked, sourced, and reviewed by our editorial team before it reaches you — because trust is earned one article at a time.',
    'From breaking news to long-form investigations, our correspondents cover politics, business, technology, culture, and everything in between, so you can stay informed no matter where you are.',
  ],

  stats: [
    { value: '2019',   label: 'Founded'           },
    { value: '120+',   label: 'Journalists'       },
    { value: '45',     label: 'Countries Covered' },
    { value: '10M+',   label: 'Monthly Readers'   },
  ],

  values: [
    {
      icon:        'bi:shield-check',
      title:       'Accuracy First',
      description: 'Every story is fact-checked and verified by our editorial team before publication. We correct mistakes openly and promptly.',
    },
    {
      icon:        'bi:eye',
      title:       'Editorial Independence',
      description: 'Our newsroom operates free from political and commercial influence, so our reporting always serves the reader, not an agenda.',
    },
    {
      icon:        'bi:globe-americas',
      title:       'Global Perspective',
      description: 'With correspondents on the ground across 45 countries, we bring context and nuance that wire reports often miss.',
    },
    {
      icon:        'bi:lightning-charge',
      title:       'Speed With Integrity',
      description: 'Breaking news moves fast, but never faster than the truth. We publish quickly without cutting corners on verification.',
    },
    {
      icon:        'bi:chat-quote',
      title:       'Diverse Voices',
      description: 'We actively seek out perspectives from underrepresented communities to tell the full story, not just the loudest one.',
    },
    {
      icon:        'bi:people',
      title:       'Reader First',
      description: 'No paywalls on public-interest reporting. Our readers come before advertisers, algorithms, or page views.',
    },
  ],

  timeline: [
    {
      year:        '2019',
      title:       'Portal News Is Founded',
      description: 'Launched by a small team of independent journalists in San Francisco with a single beat: honest, unbiased reporting.',
    },
    {
      year:        '2020',
      title:       'First International Bureau',
      description: 'Opened our first overseas bureau in London, expanding coverage of European politics and economics.',
    },
    {
      year:        '2021',
      title:       'Investigative Desk Launched',
      description: 'Formed a dedicated investigative unit, publishing our first award-nominated series on global supply chains.',
    },
    {
      year:        '2022',
      title:       'Reaching 5 Million Readers',
      description: 'Crossed 5 million monthly readers as our mobile app launched, bringing real-time alerts to a global audience.',
    },
    {
      year:        '2024',
      title:       'Press Freedom Award',
      description: 'Recognized by the International Press Institute for our coverage of press freedom violations worldwide.',
    },
    {
      year:        '2026',
      title:       'Today',
      description: 'Now operating in 45 countries with over 120 journalists, still guided by the same founding principle: report the truth.',
    },
  ],

  gallery: [
    { image: '/img/gallery/1.jpg',     alt: 'Newsroom during a live election night broadcast'  },
    { image: '/img/gallery/2.jpg',     alt: 'Correspondent filing a report from the field'      },
    { image: '/img/gallery/3.jpg',     alt: 'Editorial team in the morning story meeting'       },
    { image: '/img/gallery/4.jpg',     alt: 'Photojournalist covering a public demonstration'    },
  ],

  socials: [
    { icon: 'bi:facebook',  label: 'Facebook',  href: '#' },
    { icon: 'bi:twitter-x', label: 'X',         href: '#' },
    { icon: 'bi:instagram', label: 'Instagram', href: '#' },
    { icon: 'bi:youtube',   label: 'YouTube',   href: '#' },
    { icon: 'bi:linkedin',  label: 'LinkedIn',  href: '#' },
  ],
};
