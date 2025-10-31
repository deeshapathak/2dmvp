import React, { useState } from 'react';
import styled from 'styled-components';
import { 
  RotateCcw, 
  Share2, 
  Download, 
  Sparkles, 
  CheckCircle, 
  ArrowRight,
  Heart,
  Zap,
  Shield
} from 'lucide-react';

const ResultsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
  width: 100%;
`;

const ScoreSection = styled.div`
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 16px;
  padding: 2rem;
  color: white;
  text-align: center;
`;

const ScoreTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
`;

const ScoreValue = styled.div`
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(45deg, #fff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const ScoreDescription = styled.p`
  opacity: 0.9;
  font-size: 1.1rem;
`;

const ImagesSection = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ImageContainer = styled.div`
  text-align: center;
`;

const ImageLabel = styled.div`
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
`;

const ImageWrapper = styled.div`
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
`;

const ResultImage = styled.img`
  width: 100%;
  height: auto;
  display: block;
`;

const ImageBadge = styled.div`
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: ${props => props.type === 'before' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(34, 197, 94, 0.9)'};
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
`;

const RecommendationsSection = styled.div`
  background: #f8fafc;
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid #e2e8f0;
`;

const SectionTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const RecommendationsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const RecommendationItem = styled.div`
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
`;

const RecommendationIcon = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
`;

const RecommendationText = styled.div`
  flex: 1;
  color: #374151;
  font-weight: 500;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 2rem;
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
  
  ${props => props.variant === 'success' && `
    background: #10b981;
    color: white;
    
    &:hover {
      background: #059669;
      transform: translateY(-2px);
    }
  `}
`;

const MeasurementsSection = styled.div`
  background: white;
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid #e5e7eb;
  margin-bottom: 2rem;
`;

const MeasurementsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
`;

const MeasurementItem = styled.div`
  text-align: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
`;

const MeasurementLabel = styled.div`
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
`;

const MeasurementValue = styled.div`
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
`;

function AnalysisResults({ data, onReset }) {
  const [isSharing, setIsSharing] = useState(false);

  const handleShare = async () => {
    setIsSharing(true);
    try {
      if (navigator.share) {
        await navigator.share({
          title: 'My Rhinovate AI Analysis',
          text: `Check out my AI-powered cosmetic analysis results!`,
          url: window.location.href,
        });
      } else {
        // Fallback to copying to clipboard
        await navigator.clipboard.writeText(
          `Check out my AI-powered cosmetic analysis results at ${window.location.href}`
        );
        alert('Results copied to clipboard!');
      }
    } catch (err) {
      console.error('Error sharing:', err);
    } finally {
      setIsSharing(false);
    }
  };

  const handleDownload = () => {
    if (data.after_url) {
      const link = document.createElement('a');
      link.href = data.after_url;
      link.download = 'rhinovate-after.jpg';
      link.click();
    }
  };

  return (
    <ResultsContainer>
      {data.before_url && data.after_url && (
        <ImagesSection>
          <ImageContainer>
            <ImageLabel>Before</ImageLabel>
            <ImageWrapper>
              <ResultImage src={data.before_url} alt="Before analysis" />
              <ImageBadge type="before">Original</ImageBadge>
            </ImageWrapper>
          </ImageContainer>
          
          <ImageContainer>
            <ImageLabel>After AI Enhancement</ImageLabel>
            <ImageWrapper>
              <ResultImage src={data.after_url} alt="After analysis" />
              <ImageBadge type="after">AI Enhanced</ImageBadge>
            </ImageWrapper>
          </ImageContainer>
        </ImagesSection>
      )}

      {data.measurements && (
        <MeasurementsSection>
          <SectionTitle>
            <Shield size={24} />
            Facial Analysis
          </SectionTitle>
          <MeasurementsGrid>
            <MeasurementItem>
              <MeasurementLabel>Nose-to-IPD Ratio</MeasurementLabel>
              <MeasurementValue>{data.measurements.nose_to_ipd_ratio?.toFixed(2) || 'N/A'}</MeasurementValue>
            </MeasurementItem>
            <MeasurementItem>
              <MeasurementLabel>Chin Projection</MeasurementLabel>
              <MeasurementValue>{data.measurements.chin_projection?.toFixed(1) || 'N/A'}</MeasurementValue>
            </MeasurementItem>
            <MeasurementItem>
              <MeasurementLabel>Jaw Asymmetry</MeasurementLabel>
              <MeasurementValue>{data.measurements.jaw_asymmetry?.toFixed(1) || 'N/A'}mm</MeasurementValue>
            </MeasurementItem>
          </MeasurementsGrid>
        </MeasurementsSection>
      )}

      {data.recommendations && data.recommendations.length > 0 && (
        <RecommendationsSection>
          <SectionTitle>
            <Sparkles size={24} />
            AI Recommendations
          </SectionTitle>
          <RecommendationsList>
            {data.recommendations.map((recommendation, index) => (
              <RecommendationItem key={index}>
                <RecommendationIcon>
                  <CheckCircle size={20} />
                </RecommendationIcon>
                <RecommendationText>{recommendation}</RecommendationText>
              </RecommendationItem>
            ))}
          </RecommendationsList>
        </RecommendationsSection>
      )}

      <ActionButtons>
        <ActionButton variant="primary" onClick={handleShare} disabled={isSharing}>
          <Share2 size={20} />
          {isSharing ? 'Sharing...' : 'Share Results'}
        </ActionButton>
        
        {data.after_url && (
          <ActionButton variant="success" onClick={handleDownload}>
            <Download size={20} />
            Download After
          </ActionButton>
        )}
        
        <ActionButton variant="secondary" onClick={onReset}>
          <RotateCcw size={20} />
          Try Another Photo
        </ActionButton>
      </ActionButtons>
    </ResultsContainer>
  );
}

export default AnalysisResults;
