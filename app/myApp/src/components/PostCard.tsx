import React, { useState } from 'react';
import { IonCard, IonCardContent, IonCardHeader, IonCardTitle, IonChip , IonIcon} from '@ionic/react';
import { bookmarkOutline, bookmark } from 'ionicons/icons';

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

interface PostCardProps{
    post: Post;
    updatePost : Function
}

interface MyObject {
    [key: string]: string | undefined; // Allows any string key with a string or undefined value
  }
const PostCard: React.FC<PostCardProps> = ({post, updatePost}) => {
    
    const [seeAll, setSeeAll] = useState<Boolean>(false);
    const [loading, setLoading] = useState<Boolean>(false);

    const getText = (post: Post) => {
      let content = post?.feed_text;
      let htmlContent = post?.html_feed;
        Object.keys(post?.href_map).map(key =>{
            content = content.replace(key, "<a href="+ post?.href_map[key] +" target='_blank'>" + key  + "</a>");
        })
        if(!content || content.length <= 300) return content;
        return seeAll ? htmlContent || content : content.slice(0 ,300) + "...";
    }

    const updatePostStatus = async (post: Post, status: string) =>{
      setLoading(true);
        const updated_post = {
            ...post,
            status,
            createdAt: new Date(post.createdAt)
        }
        try {
            const response = await fetch('https://linx-server-zqc5.onrender.com/update', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(updated_post),
          }); // Replace with your API endpoint
            post = await response.json();
            updatePost(updated_post);
          } catch (error) {
            console.error('Failed to fetch posts:', error);
          }
          finally {
           setLoading(false) ;
          }
    }

  if(loading)return <IonCard><div> Loading ...</div></IonCard>;

  return (
    <IonCard>
      <IonCardHeader>
        <p><em>{new Date(post?.createdAt).toLocaleDateString()}</em></p>
        <IonCardTitle><a href={post?.profile}>{post?.poster}</a> <IonChip style={{width:"fit-post?.feed_text"}}>{post?.status}</IonChip> <button style={{ background:"transparent", lineHeight:"10px", padding:"10px", borderRadius:"5px"}} onClick={() => updatePostStatus(post, "bookmarked")}><IonIcon icon={post?.status ==="bookmarked" ? bookmark: bookmarkOutline}></IonIcon>
</button></IonCardTitle>
        <h6>{post?.poster_bio}</h6>
      </IonCardHeader>
      <IonCardContent>
        <p  dangerouslySetInnerHTML={{ __html: getText(post) }}/>
        {!seeAll ?  <p onClick={()=> setSeeAll(true)} style={{color: "white", cursor:"pointer"}}>see more</p> : null}

        {post?.status === "qualified" || post?.status === "lead"?
        <div style={{display:"flex", gap:"1rem", marginTop:"1rem", alignItems:"center"}}> <button style={{ background:"red", lineHeight:"10px", padding:"10px", borderRadius:"5px"}} onClick={() => updatePostStatus(post, "discard")}>discard</button><button style={{ background:"green", lineHeight:"10px", padding:"10px", borderRadius:"5px"}} onClick={() => updatePostStatus(post, post?.status ==="lead"?"done" : "lead")}>{post?.status ==="lead"?"Done": "Lead"}</button></div>: <button style={{ background:"green", lineHeight:"10px", padding:"10px", borderRadius:"5px"}} onClick={() => updatePostStatus(post, "qualified")}>qualified</button>}
      </IonCardContent>
    </IonCard>
  );
};

export default PostCard;
