import React from 'react';
import styled from 'styled-components';
import { Sparkles, Heart } from 'lucide-react';

const FooterContainer = styled.footer`
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2rem;
  margin-top: auto;
`;

const FooterContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  color: white;
`;

const FooterLogo = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
`;

const FooterText = styled.p`
  opacity: 0.7;
  margin-bottom: 0.5rem;
`;

const Disclaimer = styled.p`
  font-size: 0.8rem;
  opacity: 0.5;
  margin-top: 1rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.4;
`;

function Footer() {
  return (
    <FooterContainer>
      <FooterContent>
        <FooterLogo>
          <Sparkles size={20} />
          Rhinovate AI
        </FooterLogo>
        
        <FooterText>
          Powered by AI • Built with <Heart size={14} style={{ display: 'inline', margin: '0 4px' }} /> for beauty enhancement
        </FooterText>
        
        <Disclaimer>
          This is a demonstration tool for educational purposes. Results are simulated and should not be considered as medical advice. 
          Consult with qualified professionals for actual cosmetic procedures.
        </Disclaimer>
      </FooterContent>
    </FooterContainer>
  );
}

export default Footer;
