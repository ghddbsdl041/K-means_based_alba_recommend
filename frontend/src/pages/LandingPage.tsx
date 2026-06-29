import HeroSection from "../components/landing/HeroSection";
import FeatureStrip from "../components/landing/FeatureStrip";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col justify-center bg-[#F0F4FF] px-6 md:px-8 py-12">
      <HeroSection />
      <div id="features" className="mt-14">
        <FeatureStrip />
      </div>
    </div>
  );
}
