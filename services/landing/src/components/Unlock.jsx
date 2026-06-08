// import React from "react";
// import { Icons } from "../assets/images";
// import { motion } from "framer-motion";

// const Unlock = () => {
//   const floatingAnimation = {
//     y: [0, -20, 0],
//     transition: {
//       duration: 4,
//       repeat: Infinity,
//       ease: "easeInOut",
//     },
//   };

//   return (
//     <section className="w-full pt-20 pb-16 md:pt-32  bg-white flex flex-col items-center overflow-hidden">
//       <div className="w-full max-w-6xl mx-auto px-4 md:px-8 flex flex-col items-center">
//         {/* Text Content */}
//         <motion.div
//           initial={{ opacity: 0, y: 60 }}
//           whileInView={{ opacity: 1, y: 0 }}
//           viewport={{ once: true, amount: 0.4 }}
//           transition={{ duration: 0.7, ease: "easeOut" }}
//           className="text-center mb-10 md:mb-16 z-10"
//         >
//           <h2 className="text-[40px] md:text-[54px] font-bold bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF]/50 bg-clip-text text-transparent mb-5 tracking-tight leading-[1.15] font-PlusJakartaSans">
//             Unlock Your Best Look
//             <br className="hidden md:block" />
//             <span className="inline-block">With Hairlync</span>
//           </h2>

//           <motion.p
//             initial={{ opacity: 0, y: 40 }}
//             whileInView={{ opacity: 1, y: 0 }}
//             viewport={{ once: true }}
//             transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
//             className="text-[#4b5563] text-[15px] md:text-[17px] font-medium leading-relaxed max-w-[700px] mx-auto px-4 font-PlusJakartaSans"
//           >
//             Discover your ideal style with Hairlync. Our AI-powered facial and
//             hair scans analyze your features and recommend the perfect
//             hairstyles to match.
//           </motion.p>
//         </motion.div>

//         {/* Image */}
//         <div className="relative w-full flex justify-center items-center mt-4">
//           {/* Glow */}
//           <div className="absolute inset-0 bg-gradient-to-b from-transparent to-white/20 z-0 pointer-events-none rounded-full blur-[100px] opacity-60 w-3/4 h-3/4 mx-auto top-1/2 -translate-y-1/2"></div>

//           <motion.img
//             animate={floatingAnimation}
//             src={Icons.unlock}
//             alt="AI Powered Face and Hair Scan Analysis"
//             initial={{ opacity: 0, scale: 0.9, y: 80 }}
//             whileInView={{ opacity: 1, scale: 1, y: 0 }}
//             viewport={{ once: true, amount: 0.3 }}
//             transition={{ duration: 0.9, delay: 0.3, ease: "easeOut" }}
//             className="relative z-10 w-full max-w-[900px] h-auto object-contain hover:scale-[1.02] transition-transform duration-700 ease-in-out"
//           />
//         </div>
//       </div>
//     </section>
//   );
// };

// export default Unlock;

import React from "react";
import { Icons } from "../assets/images";
import { motion, useScroll, useTransform } from "framer-motion";

const Unlock = () => {
  // Floating + breathing animation
  const floatingAnimation = {
    y: [0, -15, 0],
    scale: [1, 1.02, 1],
    transition: {
      duration: 5,
      repeat: Infinity,
      ease: "easeInOut",
    },
  };

  // Stagger text animation
  const container = {
    hidden: {},
    show: {
      transition: {
        staggerChildren: 0.15,
      },
    },
  };

  const item = {
    hidden: { opacity: 0, y: 40 },
    show: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] },
    },
  };

  // Subtle parallax scroll effect
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, -50]);

  return (
    <section className="w-full pt-20 pb-16 md:pt-32 bg-white flex flex-col items-center overflow-hidden">
      <div className="w-full max-w-6xl mx-auto px-4 md:px-8 flex flex-col items-center">
        {/* Text Content */}
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
          className="text-center mb-10 md:mb-16 z-10"
        >
          <motion.h2
            variants={item}
            className="text-[40px] md:text-[54px] font-bold bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF]/50 bg-clip-text text-transparent mb-5 tracking-tight leading-[1.15] font-PlusJakartaSans"
          >
            Unlock Your Best Look
            <br className="hidden md:block" />
            <span className="inline-block">With Hairlync</span>
          </motion.h2>

          <motion.p
            variants={item}
            className="text-[#4b5563] text-[15px] md:text-[17px] font-medium leading-relaxed max-w-[700px] mx-auto px-4 font-PlusJakartaSans"
          >
            Discover your ideal style with Hairlync. Our AI-powered facial and
            hair scans analyze your features and recommend the perfect
            hairstyles to match.
          </motion.p>
        </motion.div>

        {/* Image */}
        <div className="relative w-full flex justify-center items-center mt-4">
          {/* Animated Glow */}
          <motion.div
            animate={{ opacity: [0.5, 0.8, 0.5], scale: [1, 1.1, 1] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="absolute inset-0 bg-gradient-to-b from-transparent to-white/20 z-0 pointer-events-none rounded-full blur-[100px] opacity-60 w-3/4 h-3/4 mx-auto top-1/2 -translate-y-1/2"
          />

          <motion.img
            animate={floatingAnimation}
            style={{ y }}
            src={Icons.unlock}
            alt="AI Powered Face and Hair Scan Analysis"
            initial={{ opacity: 0, scale: 0.9, y: 80 }}
            whileInView={{ opacity: 1, scale: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.9, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            whileHover={{
              scale: 1.03,
              rotate: 0.5,
            }}
            className="relative z-10 w-full max-w-[900px] h-auto object-contain transition-transform duration-700 ease-in-out"
          />
        </div>
      </div>
    </section>
  );
};

export default Unlock;
