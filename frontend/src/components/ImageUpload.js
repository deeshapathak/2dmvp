import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';
import { Camera, Upload, Loader, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { API_URL } from '../config';

const UploadContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
`;

const DropzoneContainer = styled.div`
  border: 2px dashed ${props => props.isDragActive ? '#667eea' : '#d1d5db'};
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.isDragActive ? 'rgba(102, 126, 234, 0.05)' : 'transparent'};
  width: 100%;
  max-width: 500px;
  
  &:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
  }
`;

const UploadIcon = styled.div`
  width: 80px;
  height: 80px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: white;
`;

const UploadText = styled.div`
  color: #374151;
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
`;

const UploadSubtext = styled.div`
  color: #6b7280;
  font-size: 0.9rem;
`;

const FileInput = styled.input`
  display: none;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  
  ${props => props.variant === 'primary' && `
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
  `}
  
  ${props => props.variant === 'secondary' && `
    background: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
    
    &:hover {
      background: #e5e7eb;
    }
  `}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
`;

const LoadingText = styled.div`
  color: #374151;
  font-weight: 500;
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const PreviewImage = styled.img`
  max-width: 300px;
  max-height: 300px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
`;

function ImageUpload({ onAnalysisComplete, isLoading, setIsLoading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 1,
    disabled: isLoading
  });

  const handleCameraCapture = () => {
    // In a real app, this would open the camera
    // For now, we'll just trigger the file input
    document.getElementById('camera-input').click();
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onAnalysisComplete(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setError(null);
  };

  if (isLoading) {
    return (
      <LoadingContainer>
        <Loader size={48} className="animate-spin" style={{ color: '#667eea' }} />
        <LoadingText>Analyzing your facial features...</LoadingText>
        <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>
          This may take a few moments
        </div>
      </LoadingContainer>
    );
  }

  return (
    <UploadContainer>
      {!selectedFile ? (
        <>
          <DropzoneContainer {...getRootProps()} isDragActive={isDragActive}>
            <input {...getInputProps()} />
            <UploadIcon>
              <Upload size={32} />
            </UploadIcon>
            <UploadText>
              {isDragActive ? 'Drop your photo here' : 'Drag & drop your photo here'}
            </UploadText>
            <UploadSubtext>
              or click to browse files
            </UploadSubtext>
          </DropzoneContainer>

          <ButtonGroup>
            <ActionButton variant="secondary" onClick={handleCameraCapture}>
              <Camera size={20} />
              Take Selfie
            </ActionButton>
            <FileInput
              id="camera-input"
              type="file"
              accept="image/*"
              capture="user"
              onChange={(e) => {
                if (e.target.files[0]) {
                  onDrop([e.target.files[0]]);
                }
              }}
            />
          </ButtonGroup>
        </>
      ) : (
        <>
          <PreviewImage src={preview} alt="Selected photo" />
          <ButtonGroup>
            <ActionButton variant="primary" onClick={handleAnalyze}>
              <Upload size={20} />
              Analyze Photo
            </ActionButton>
            <ActionButton variant="secondary" onClick={handleReset}>
              Choose Different Photo
            </ActionButton>
          </ButtonGroup>
        </>
      )}

      {error && (
        <ErrorMessage>
          <AlertCircle size={20} />
          {error}
        </ErrorMessage>
      )}
    </UploadContainer>
  );
}

export default ImageUpload;
