import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Backdrop, CircularProgress, TextField, Button } from "@mui/material";
import "./imagevideo.css";
import PromptPage from "./PromptPage";
function ImageVideoPage() {
  const { state } = useLocation();
  const prompt = state?.prompt || "";
  const [query, setQuery] = useState();
  const [inputValue, setInputValue] = useState();
  const [images, setImages] = useState([]);
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [retryImageCount, setRetryImageCount] = useState(0);
  const [retryVideoCount, setRetryVideoCount] = useState(0);

  const fetchImages = async () => {
    if (!query?.trim()) return;
    setError(null);
    setIsLoading(true);
    try {
      const response = await fetch("http://172.16.30.100:6743/image-search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const imageData = await response.json();
      const fetchedImages = imageData?.images.map((item) => ({
        imgSrc: item.img_src,
        url: item.url,
        title: item.title,
      }));

      setImages(fetchedImages);
      setIsLoading(false);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch images. Please try again.");
      setIsLoading(false);
    }
  };

  const fetchVideos = async () => {
    if (!query?.trim()) return;
    setError(null);
    setIsLoading(true);
    try {
      const response = await fetch("http://172.16.30.100:6743/video-search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const videoData = await response.json();
      const fetchedVideos = videoData.videos.slice(0, 20);
      setVideos(fetchedVideos);
      setIsLoading(false);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch videos. Please try again.");
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    console.log(query);

    setQuery(query.trim());
    if (query.trim()) {
      fetchImages();
      fetchVideos();
    }
  };

  return (
    <div className='App'>
      <div className='promptpage'>
        <PromptPage />
      </div>
      <div className='search-container'>
        <h2>Search for Images and Videos</h2>

        {/* Search Input Field */}
        <div className='search-bar'>
          <TextField
            label='Search Query'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            variant='outlined'
            fullWidth
          />
          <Button
            variant='contained'
            color='primary'
            onClick={handleSearch}
            style={{ marginTop: "10px" }}
          >
            Search
          </Button>
        </div>

        {/* Display Results */}
        <div className='results'>
          <h3>Images</h3>
          <div className='images'>
            {images.length > 0 ? (
              images.map((image, index) => (
                <div key={index} className='image-item'>
                  <img src={image.imgSrc} alt={`Result ${index + 1}`} />
                </div>
              ))
            ) : (
              <p>No images found.</p>
            )}
          </div>

          <h3>Videos</h3>
          <div className='videos'>
            {videos.length > 0 ? (
              videos.map((video, index) => (
                <div key={index}>
                  <iframe
                    src={video.iframe_src}
                    title={video.title}
                    width='560'
                    height='315'
                    frameBorder='0'
                    allow='accelerometer; encrypted-media; gyroscope; picture-in-picture'
                    allowFullScreen
                  ></iframe>
                </div>
              ))
            ) : (
              <p>No videos found.</p>
            )}
          </div>
        </div>
      </div>

      {/* Loading Indicator */}
      <Backdrop sx={{ color: "#fff", zIndex: 1 }} open={isLoading}>
        <CircularProgress color='inherit' />
      </Backdrop>
    </div>
  );
}

export default ImageVideoPage;
