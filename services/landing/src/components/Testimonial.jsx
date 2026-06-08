import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const testimonials = [
  {
    name: "Neil Sims",
    avatar: "https://i.pravatar.cc/150?img=11",
    title: "Hairlync is a game changer for my salon",
    quote:
      '"Hairlync has revolutionized my salon. The AI-driven analysis is spot-on, and my clients are thrilled with the accurate style recommendations. It\'s like having a personal style consultant for every client!"',
  },
  {
    name: "Micheal Gough",
    avatar: "https://i.pravatar.cc/150?img=12",
    title: "The ultimate tool for modern salons",
    quote:
      '"Hairlync is a game-changer! The AI algorithms provide personalized style recommendations that my clients adore. It\'s intuitive, efficient, and has significantly boosted client satisfaction. A must-have for any salon!"',
  },
  {
    name: "Helene Engels",
    avatar: "https://i.pravatar.cc/150?img=5",
    title: "Streamlined our consultation process",
    quote:
      '"Hairlync has transformed my approach to client consultations. The AI-driven face analysis and style recommendations save time and ensure client satisfaction. It\'s an indispensable tool for any stylist looking to stay ahead."',
  },
  {
    name: "Karen Nelson",
    avatar: "https://i.pravatar.cc/150?img=42",
    title: "My clients love the virtual try-ons",
    quote:
      "\"Hairlync has elevated my salon's service. The virtual try-ons are a hit, and the AI-powered style suggestions are incredibly accurate. It's a fantastic way to enhance the client experience and drive repeat business.\"",
  },
  {
    name: "Sarah Jenkins",
    avatar: "https://i.pravatar.cc/150?img=47",
    title: "Incredible AI-driven insights",
    quote:
      '"We\'ve seen a 30% increase in customer satisfaction thanks to Hairlync. Being able to visualize their look before the cut has completely removed the guesswork. Absolutely brilliant platform."',
  },
  {
    name: "Marcus Cole",
    avatar: "https://i.pravatar.cc/150?img=60",
    title: "The future of hair styling",
    quote:
      '"Hairlync brings an unmatched level of professionalism to our salon. The detailed hair analysis gives us confidence to offer premium tier services and the clients keep coming back for more."',
  },
];

const Testimonial = () => {
  const [visibleCount, setVisibleCount] = useState(4);

  const getBorders = (index, total) => {
    let classes = "border-gray-100 ";

    // Right border on desktop for every even index (left column in 2x2 or 3x2)
    if (index % 2 === 0) {
      classes += "md:border-r ";
    }

    // Bottom border on desktop for all EXCEPT the last two items (last row)
    if (index < total - 2) {
      classes += "md:border-b ";
    }

    // Bottom border on mobile for all EXCEPT the very last item
    if (index < total - 1) {
      classes += "max-md:border-b ";
    }

    return classes.trim();
  };

  const currentTestimonials = testimonials.slice(0, visibleCount);

  return (
    <section className="py-16 md:py-24 bg-white font-sans max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center mb-16 flex flex-col items-center">
        <div className="relative inline-flex items-center justify-center">
          <h2 className="text-[36px] md:text-[52px] font-bold mb-5 leading-[1.2] tracking-tight text-gradient-testimonial">
            Testimonials
          </h2>
        </div>
        <p className="text-[#6B7280] text-[17px] md:text-[19px] font-medium mt-6 leading-relaxed">
          Read why stylists and clients love Hairlync's AI-driven hair
          <br className="hidden md:block" /> transformation experience.
        </p>
      </div>

      {/* Grid */}
      <motion.div
        layout
        className="grid grid-cols-1 md:grid-cols-2 transition-all duration-500 ease-in-out"
      >
        <AnimatePresence mode="popLayout">
          {currentTestimonials.map((test, index) => (
            <motion.div
              layout
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{
                duration: 0.5,
                delay: index >= 4 ? (index - 4) * 0.25 : index * 0.25,
              }}
              key={index}
              className={`p-8 md:p-14 flex flex-col items-center text-center ${getBorders(index, visibleCount)}`}
            >
              <div className="flex items-center justify-center space-x-3 mb-5">
                <img
                  src={test.avatar}
                  alt={test.name}
                  className="w-8 h-8 md:w-9 md:h-9 rounded-full object-cover shadow-sm"
                />
                <span className="font-bold text-[#1F2937] text-[16px] md:text-[17px] tracking-wide">
                  {test.name}
                </span>
              </div>
              <h3 className="text-lg md:text-[21px] font-bold text-[#374151] mb-5 tracking-tight">
                {test.title}
              </h3>
              <p className="text-[#6B7280] text-[15px] md:text-[16px] leading-relaxed font-medium">
                {test.quote}
              </p>
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>

      {/* Show more button */}
      {visibleCount < testimonials.length && (
        <div className="flex justify-center mt-12 md:mt-16">
          <button
            onClick={() => setVisibleCount(testimonials.length)}
            className="px-6 py-2.5 bg-white border border-[#E5E7EB] text-[#374151] text-[14px] font-semibold rounded-lg shadow-[0_1px_3px_rgba(0,0,0,0.05)] hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#7D9BF7] cursor-pointer"
          >
            Show more...
          </button>
        </div>
      )}
    </section>
  );
};

export default Testimonial;
