import { getCollection } from 'astro:content';

export const GET = async () => {
  const allPosts = (await getCollection('blog').catch(() => [])) ?? [];

  const posts = allPosts.sort(
    (a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime()
  );

  const index = posts.map((post) => ({
    id:       post.id,
    title:    post.data.title,
    excerpt:  post.data.excerpt,
    category: post.data.category,
    tags:     post.data.tags ?? [],
    date:     post.data.date,
    cover:    post.data.cover,
    authorId: post.data.authorId,
    readTime: post.data.readTime,
    url:      `/${post.id}`,
  }));

  return new Response(JSON.stringify(index), {
    headers: { 'Content-Type': 'application/json' },
  });
};