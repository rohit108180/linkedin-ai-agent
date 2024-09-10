import React, { useState, useEffect } from 'react';
import { IonContent, IonPage, IonLoading } from '@ionic/react';
import PostCard from '../components/PostCard';
import { IonItem, IonSelect, IonSelectOption } from '@ionic/react';
import { IonDatetime, IonDatetimeButton, IonModal } from '@ionic/react';
interface MyObject {
  [key: string]: string | undefined; // Allows any string key with a string or undefined value
}
interface Post {
  _id: string;
  poster: string;
  poster_bio: string;
  profile: string;
  feed_text: string;
  html_feed: string;
  status: string;
  href_map: MyObject;
  createdAt: string;
}

interface Filter {
  [key: string]: string | undefined;
}
  

const PostsList: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filter, setFilter] = useState<Filter>({});
  const fetchPosts = async () => {
    setLoading(true)
    try {
      const response = await fetch('https://linx-server-zqc5.onrender.com/posts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filter),
    }); // Replace with your API endpoint
      let data = await response.json();
      // sort
      data = data.sort((post1: Post, post2: Post) => (new Date(post2.createdAt).getTime() - new Date(post1.createdAt).getTime()));
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

  const handleSelectChange = (e: any) => {
    const value = e.detail.value;
    setFilter({
      ...filter,
      status: value
    })
  };

  const handleFilterDate = (e: any) => {
    let value = e.detail.value;
    value = value?.slice(0, 10)
    setFilter({
      ...filter,
      date: value
    })
  };

  const updatePost = (post :Post) =>{
    console.log(post)
    let tempPost = structuredClone(posts);
    tempPost.map( (postOld) =>{
      if(postOld._id == post._id){
         return post;
      }
      return postOld;
    })
    setPosts([
      post,
      ...posts.filter(postOld => postOld._id !== post._id)
    ]);
  }
  

  if (loading) {
    return <IonLoading isOpen={loading} message={'Loading posts...'} />;
  }

  return (
    <IonPage>
    <div style={{display:'flex', justifyContent:"space-between"}}>
      <IonItem style={{width:"100%", maxWidth:"200px"}} >
        <IonSelect interface="action-sheet" placeholder="Qualified" onIonChange={handleSelectChange} value={filter?.status}>
          <IonSelectOption value="qualified">Qualified</IonSelectOption>
          <IonSelectOption value="pending">Pending</IonSelectOption>
          <IonSelectOption value="unqualified">Unqualified</IonSelectOption>
          <IonSelectOption value="bookmarked">Save For Later</IonSelectOption>
          <IonSelectOption value="discard">Discarded</IonSelectOption>
          <IonSelectOption value="done">Completed</IonSelectOption>
          <IonSelectOption value="lead">Lead</IonSelectOption>
        </IonSelect>
      </IonItem>
      
      <IonDatetimeButton datetime="datetime" style={{width:"fit-content", margin:"1rem"}}></IonDatetimeButton >

      <IonModal keepContentsMounted={true}>
        <IonDatetime id="datetime" onIonChange={handleFilterDate} value={filter?.date} ></IonDatetime>
      </IonModal>
    </div>
      <IonContent>
        {posts?.length ? posts.map((post) => (
          <PostCard
            key={post._id}
            post={post}
            updatePost = {updatePost}
          />
        )): "No Posts"}
      </IonContent>
    </IonPage>
  );
};

export default PostsList;
