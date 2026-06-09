import HeroSection from "../components/landing/HeroSection";
import FeatureStrip from "../components/landing/FeatureStrip";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
      <HeroSection />
      <FeatureStrip />
    </div>
  );
}
