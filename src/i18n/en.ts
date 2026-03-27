// English translation strings
export const en = {
  lang: 'en',
  locale: 'en-US' as const,

  nav: {
    home: 'Home',
    news: 'News',
    about: 'About',
  },

  home: {
    featuredLabel: 'Featured',
    readMore: 'Read More',
    loadMore: 'Load More',
    loading: 'Loading...',
    sidebarCategories: 'Categories',
    sidebarAds: 'Advertising',
    sidebarStats: 'Statistics',
    sidebarRecommended: '🎯 Recommended',
    adSlot1Title: 'Advertise Here',
    adSlot1Sub: 'Targeted Traffic · High Conversion',
    adSlot2Sub: 'Under Review...',
    statsArticles: 'Articles',
    statsCategories: 'Categories',
    statsRss: 'RSS Feeds',
    statsUptime: 'Uptime',
    updating: 'Updating...',
  },

  footer: {
    aboutUs: 'About Us',
    contact: 'Contact',
    privacy: 'Privacy Policy',
    terms: 'Terms of Service',
    advertise: 'Advertising',
    poweredBy: 'MollySpace',
  },

  date: {
    today: 'Today',
    yesterday: 'Yesterday',
    daysAgo: (n: number) => `${n}d ago`,
    latest: 'Latest',
  },
} as const;

export type EnI18n = typeof en;
