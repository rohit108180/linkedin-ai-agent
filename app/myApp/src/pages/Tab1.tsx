import React, { useState, useEffect } from 'react';
import { IonContent, IonPage, IonLoading } from '@ionic/react';
import PostCard from '../components/PostCard';

interface MyObject {
  [key: string]: string | undefined; // Allows any string key with a string or undefined value
}
interface Post {
  _id: string;
  poster: string;
  poster_bio: string;
  profile: string;
  feed_text: string;
  status: string;
  href_map: MyObject;
  createdAt: string;
}
  

const PostsList: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filter, setFilter] = useState<Object>({});
  const fetchPosts = async () => {
    try {
      const response = await fetch('https://linkedin-xtream.onrender.com/posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filter),
    }); // Replace with your API endpoint
      let data = await response.json();
      // sort
      data = data.sort((post1: Post, post2: Post) => (new Date(post2.createdAt).getTime() - new Date(post1.createdAt).getTime()));

      console.log(data);
      console.log(data);
      setPosts(data);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchPosts();
  }, [filter]);

  if (loading) {
    return <IonLoading isOpen={loading} message={'Loading posts...'} />;
  }

  return (
    <IonPage>
      <IonContent>
        {posts.map((post) => (
          <PostCard
            key={post._id}
            post={post}
          />
        ))}
      </IonContent>
    </IonPage>
  );
};

export default PostsList;
