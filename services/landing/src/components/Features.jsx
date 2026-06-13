// with framer-motion
import React from "react";
import { Icons } from "../assets/images";
import { motion } from "framer-motion";

const Features = () => {
  return (
    <section className="relative w-full py-16 bg-white overflow-hidden flex flex-col items-center h-screen  justify-start">
      {/* Background */}
      <div
        className="absolute inset-0 z-0 opacity-80 bg-cover bg-center bg-no-repeat pointer-events-none"
        style={{ backgroundImage: `url(${Icons.featureBg})` }}
      />

      <div className="relative z-10 w-full max-w-[1440px] mx-auto px-4 md:px-8">
        {/* Header */}
        <div className="text-center mb-10 md:mb-20">
          <h2 className="text-4xl mt-16 md:text-[54px] font-bold mb-4 leading-tight text-gradient-feature font-PlusJakartaSans">
            App Features
          </h2>
        </div>
        {/* image section  */}
        <div className="relative flex flex-col items-center justify-center w-full lg:min-h-[650px]">
          {/* Image */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 60 }}
            whileInView={{ opacity: 1, scale: 1, y: 0 }}
            viewport={{ once: true, amount: 0.4 }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
            className="relative -mt-24 lg:-mt-48 w-full max-w-4xl flex justify-center items-center z-10 lg:mb-12"
          >
            <img
              src={Icons.feature}
              alt="App Features Walkthrough"
              className="w-full h-auto object-contain"
            />
          </motion.div>

          {/* card seciton  */}

          {/* Left Card */}

          <motion.div
            initial={{ opacity: 0, x: -120 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.4 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.4 }}
            className="lg:absolute left-0 2xl:left-40 lg:top-[55%] lg:-translate-y-1/2 z-20
  mt-8 lg:mt-0
  bg-white/20 backdrop-blur-xl
  border border-white/30
  rounded-lg
  p-3 md:p-4
  shadow-[0_8px_32px_rgba(31,38,135,0.2)]
  w-full max-w-[270px]
  text-center text-[#383838] text-sm  leading-relaxed
  transform hover:-translate-y-2 transition-all duration-300 ease-out
  before:content-[''] before:absolute before:inset-0
  before:rounded-lg before:bg-gradient-to-b
  before:from-white/20 before:to-transparent before:opacity-30"
          >
            Get instant hair insights, quick stats, and AI-powered face analysis
            all in one intelligent dashboard.
          </motion.div>

          {/* Bottom Card */}
          <motion.div
            initial={{ opacity: 0, y: 120 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.4 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.7 }}
            className="lg:absolute bottom-0 2xl:bottom-20  z-30
            mt-8 lg:mt-0
            bg-white/20 backdrop-blur-sm rounded-lg
            p-3 md:p-4 shadow-[0_3px_6px_0px_rgba(0,0,0,0.16)]
            w-full max-w-[270px] text-center text-[#383838] text-sm  leading-relaxed transform hover:-translate-y-2 transition-all duration-400 ease-out"
          >
            Choose your journey. Whether client or professional, Hair adapts
            with a tailored, smart onboarding experience.
          </motion.div>

          {/* Right Card */}
          <motion.div
            initial={{ opacity: 0, x: 120 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.4 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 1 }}
            className="lg:absolute right-0 2xl:right-40 lg:top-[49%]
            mt-8 lg:mt-0
            bg-white/10 backdrop-blur-sm rounded-lg border-[.5px] border-white
            p-3 md:p-4 shadow-[0_3px_6px_0px_rgba(0,0,0,0.16)]
            w-full max-w-[270px] text-center text-[#383838] text-sm  leading-relaxed transform hover:-translate-y-2 transition-all duration-400 ease-out"
          >
            Find the right expert, explore services, and book appointments in
            seconds powered by AI-driven suggestions.
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Features;

// with animation and image blur

// import React from "react";
// import { Icons } from "../assets/images";
// import { motion } from "framer-motion";

// const Features = () => {
//   return (
//     <section className="relative w-full py-16 bg-white overflow-hidden flex flex-col items-center h-screen justify-center">
//       {/* Background */}
//       <div
//         className="absolute inset-0 z-0 opacity-80 bg-cover bg-center bg-no-repeat pointer-events-none"
//         style={{ backgroundImage: `url(${Icons.featureBg})` }}
//       />

//       <div className="relative z-10 w-full max-w-[1440px] mx-auto px-4 md:px-8">
//         {/* Header */}
//         <div className="text-center mb-10 md:mb-20">
//           <h2 className="text-4xl mt-16 md:text-[54px] font-bold mb-4 leading-tight text-gradient-feature font-PlusJakartaSans">
//             App Features
//           </h2>
//         </div>

//         {/* image section  */}
//         <div className="relative flex flex-col items-center justify-center w-full lg:min-h-[650px]">
//           {/* Image with Animation */}
//           <motion.div
//             initial={{ opacity: 0, scale: 0.85, y: 80 }}
//             whileInView={{ opacity: 1, scale: 1, y: 0 }}
//             viewport={{ once: true, amount: 0.4 }}
//             transition={{ duration: 1, ease: "easeOut" }}
//             className="relative -mt-24 lg:-mt-48 w-full max-w-4xl flex justify-center items-center z-10 lg:mb-12"
//           >
//             {/* Glow Background */}
//             <motion.div
//               animate={{
//                 scale: [1, 1.05, 1],
//                 opacity: [0.4, 0.6, 0.4],
//               }}
//               transition={{
//                 duration: 6,
//                 repeat: Infinity,
//                 ease: "easeInOut",
//               }}
//               className="absolute w-[120%] h-[120%] bg-gradient-to-r from-purple-400/20 via-pink-300/20 to-blue-300/20 blur-3xl rounded-full z-0"
//             />

//             {/* Floating Image */}
//             <motion.img
//               src={Icons.feature}
//               alt="App Features Walkthrough"
//               className="w-full h-auto object-contain relative z-10"
//               animate={{
//                 y: [0, -10, 0],
//               }}
//               transition={{
//                 duration: 4,
//                 repeat: Infinity,
//                 ease: "easeInOut",
//               }}
//             />
//           </motion.div>

//           {/* Left Card */}
//           <motion.div
//             initial={{ opacity: 0, x: -120 }}
//             whileInView={{ opacity: 1, x: 0 }}
//             viewport={{ once: true, amount: 0.4 }}
//             transition={{ duration: 0.6, ease: "easeOut", delay: 0.4 }}
//             className="lg:absolute left-0 2xl:left-40 lg:top-[55%] lg:-translate-y-1/2 z-20
//             mt-8 lg:mt-0
//             bg-white/20 backdrop-blur-xl
//             border border-white/30
//             rounded-lg
//             p-3 md:p-4
//             shadow-[0_8px_32px_rgba(31,38,135,0.2)]
//             w-full max-w-[270px]
//             text-center text-[#383838] text-sm leading-relaxed
//             transform hover:-translate-y-2 transition-all duration-300 ease-out
//             before:content-[''] before:absolute before:inset-0
//             before:rounded-lg before:bg-gradient-to-b
//             before:from-white/20 before:to-transparent before:opacity-30"
//           >
//             Get instant hair insights, quick stats, and AI-powered face analysis
//             all in one intelligent dashboard.
//           </motion.div>

//           {/* Bottom Card */}
//           <motion.div
//             initial={{ opacity: 0, y: 120 }}
//             whileInView={{ opacity: 1, y: 0 }}
//             viewport={{ once: true, amount: 0.4 }}
//             transition={{ duration: 0.6, ease: "easeOut", delay: 0.7 }}
//             className="lg:absolute bottom-0 2xl:bottom-20 z-30
//             mt-8 lg:mt-0
//             bg-white/20 backdrop-blur-sm rounded-lg
//             p-3 md:p-4 shadow-[0_3px_6px_0px_rgba(0,0,0,0.16)]
//             w-full max-w-[270px] text-center text-[#383838] text-sm leading-relaxed
//             transform hover:-translate-y-2 transition-all duration-400 ease-out"
//           >
//             Choose your journey. Whether client or professional, Hiar adapts
//             with a tailored, smart onboarding experience.
//           </motion.div>

//           {/* Right Card */}
//           <motion.div
//             initial={{ opacity: 0, x: 120 }}
//             whileInView={{ opacity: 1, x: 0 }}
//             viewport={{ once: true, amount: 0.4 }}
//             transition={{ duration: 0.6, ease: "easeOut", delay: 1 }}
//             className="lg:absolute right-0 2xl:right-40 lg:top-[49%]
//             mt-8 lg:mt-0
//             bg-white/10 backdrop-blur-sm rounded-lg border-[.5px] border-white
//             p-3 md:p-4 shadow-[0_3px_6px_0px_rgba(0,0,0,0.16)]
//             w-full max-w-[270px] text-center text-[#383838] text-sm leading-relaxed
//             transform hover:-translate-y-2 transition-all duration-400 ease-out"
//           >
//             Find the right expert, explore services, and book appointments in
//             seconds powered by AI-driven suggestions.
//           </motion.div>
//         </div>
//       </div>
//     </section>
//   );
// };

// export default Features;
