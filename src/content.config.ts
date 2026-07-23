import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    cover: z.string(),
    date: z.string(),
    category: z.string(),
    tags: z.array(z.string()).optional().default([]),
    readTime: z.number(),
    featured: z.boolean().optional().default(false),
    trending: z.boolean().optional().default(false),
    popular: z.boolean().optional().default(false),
    authorId: z.string(),
    excerpt: z.string(),
    sponsored: z.boolean().optional().default(false),
    sponsorName: z.string().optional(),
    showDisclosure: z.boolean().optional().default(false),
    lifeStage: z.array(z.string()).optional().default([]),
  }),
});

const pages = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/pages' }),
  schema: z.object({
    title: z.string(),
    label: z.string(),
    icon: z.string(),
    date: z.string(),
    description: z.string().optional(),
  }),
});

export const collections = { blog, pages };
