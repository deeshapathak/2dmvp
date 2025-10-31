import React, { useState } from 'react';
import styled from 'styled-components';
import { Sparkles, Shield, Zap } from 'lucide-react';
import ImageUpload from './components/ImageUpload';
import AnalysisResults from './components/AnalysisResults';
import Header from './components/Header';
import Footer from './components/Footer';

const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
`;

const HeroSection = styled.section`
  text-align: center;
  margin-bottom: 3rem;
  color: white;
`;

const HeroTitle = styled.h1`
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #fff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
`;

const HeroSubtitle = styled.p`
  font-size: 1.25rem;
  font-weight: 300;
  margin-bottom: 2rem;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
`;

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  margin-bottom: 3rem;
  width: 100%;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FeatureCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  }
`;

const FeatureIcon = styled.div`
  width: 60px;
  height: 60px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: white;
`;

const FeatureTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
`;

const FeatureDescription = styled.p`
  font-size: 0.9rem;
  opacity: 0.8;
  line-height: 1.5;
`;

const UploadSection = styled.section`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 3rem;
  width: 100%;
  max-width: 800px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
`;

const SectionTitle = styled.h2`
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin-bottom: 1rem;
`;

const SectionSubtitle = styled.p`
  color: #6b7280;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.1rem;
`;

function App() {
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
  };

  const handleReset = () => {
    setAnalysisData(null);
  };

  return (
    <AppContainer>
      <Header />
      <MainContent>
        <HeroSection>
          <HeroTitle>Rhinovate AI</HeroTitle>
          <HeroSubtitle>
            Discover your best self with AI-powered cosmetic analysis. 
            See realistic results of procedures like rhinoplasty, lip filler, and more.
          </HeroSubtitle>
          
          <FeaturesGrid>
            <FeatureCard>
              <FeatureIcon>
                <Sparkles size={24} />
              </FeatureIcon>
              <FeatureTitle>AI-Powered Analysis</FeatureTitle>
              <FeatureDescription>
                Advanced facial analysis using computer vision to identify enhancement opportunities
              </FeatureDescription>
            </FeatureCard>
            
            <FeatureCard>
              <FeatureIcon>
                <Shield size={24} />
              </FeatureIcon>
              <FeatureTitle>Medical-Grade Precision</FeatureTitle>
              <FeatureDescription>
                Based on established beauty standards and facial harmony principles
              </FeatureDescription>
            </FeatureCard>
            
            <FeatureCard>
              <FeatureIcon>
                <Zap size={24} />
              </FeatureIcon>
              <FeatureTitle>Instant Results</FeatureTitle>
              <FeatureDescription>
                Get your personalized analysis and before/after preview in seconds
              </FeatureDescription>
            </FeatureCard>
          </FeaturesGrid>
        </HeroSection>

        <UploadSection>
          <SectionTitle>Upload Your Photo</SectionTitle>
          <SectionSubtitle>
            Take a selfie or upload a clear front-facing photo to get started
          </SectionSubtitle>
          
          {!analysisData ? (
            <ImageUpload 
              onAnalysisComplete={handleAnalysisComplete}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
            />
          ) : (
            <AnalysisResults 
              data={analysisData}
              onReset={handleReset}
            />
          )}
        </UploadSection>
      </MainContent>
      <Footer />
    </AppContainer>
  );
}

export default App;
