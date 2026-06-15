export interface SiteConfig {
  name: string;
  tagline: string;
  location: string;
  github: string;
  twitter: string;
  email: string;
  now_text: string;
}

export interface Article {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content: string;
  category: string;
  tags: string;
  read_time_min: number;
  featured: boolean;
  published: boolean;
  created_at: string;
  updated_at: string;
}

export interface PhotoLink {
  id: number;
  title: string;
  instagram_url: string;
  category: string;
  sort_order: number;
  created_at: string;
}

export interface Project {
  id: number;
  title: string;
  description: string;
  url: string;
  status: string;
  tech_tags: string;
  icon_color: string;
  sort_order: number;
}

export interface StartupIdea {
  id: number;
  title: string;
  description: string;
  contact_url: string;
  sort_order: number;
}

export interface DayEntry {
  id: number;
  entry_date: string;
  personal: string;
  professional: string;
  created_at: string;
  updated_at: string;
}

export interface IdentityCard {
  id: number;
  category: string;
  content: string;
  updated_at: string;
}
