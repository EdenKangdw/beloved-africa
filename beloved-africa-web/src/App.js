import React, { useState } from "react";
import "./App.css";

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [files, setFiles] = useState([]);

  const handleFileChange = async (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) {
      alert("파일을 선택해주세요.");
      return;
    }

    console.log("파일 업로드:", selectedFile.name);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/africa/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        alert(`파일 업로드 성공: ${data.filename}`);

        // Fetch thumbnail data from the server
        const thumbnailResponse = await fetch(
          `http://localhost:8000/africa/thumbnail/${data.thumbnail
            .split("/")
            .pop()}`
        );
        if (thumbnailResponse.ok) {
          const thumbnailData = await thumbnailResponse.json();

          setFiles((prevFiles) => [
            ...prevFiles,
            {
              id: prevFiles.length + 1,
              name: data.filename,
              thumbnail: thumbnailData.thumbnail,
              thumbnailDownloadUrl: `http://localhost:8000/africa/download/${data.thumbnail
                .split("/")
                .pop()}`,
            },
          ]);
        } else {
          console.error(
            "썸네일 가져오기 실패:",
            await thumbnailResponse.text()
          );
          alert("썸네일 가져오기 실패");
        }
        console.log(data);
      } else {
        const errorMsg = await response.text();
        console.error("업로드 실패:", errorMsg);
        alert(`업로드 실패: ${errorMsg}`);
      }
    } catch (error) {
      console.error("업로드 에러:", error);
      alert("업로드 중 오류가 발생했습니다.");
    }
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const filteredFiles = files.filter((file) =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="container">
      <input
        type="file"
        id="file-upload"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
      <button
        className="upload-btn"
        onClick={() => document.getElementById("file-upload").click()}
      >
        파일 업로드
      </button>

      <input
        type="text"
        className="search-bar"
        placeholder="검색..."
        value={searchTerm}
        onChange={handleSearch}
      />

      <div className="file-list">
        {filteredFiles.map((file) => (
          <div className="file-item" key={file.id}>
            <img src={file.thumbnail} alt="thumbnail" className="thumbnail" />
            <div className="file-name">{file.name}</div>
            <a href={file.thumbnailDownloadUrl} download>
              <button className="download-btn">다운로드</button>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
