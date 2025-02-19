import { useState, useEffect } from 'react';
import axios from 'axios';

export default function useFetch(url) {
  const [data, setData] = useState(null);
  useEffect(() => {
    axios.get(url)
      .then(response => setData(response.data))
      .catch(error => console.error("Fetch error:", error));
  }, [url]);
  return data;
}
