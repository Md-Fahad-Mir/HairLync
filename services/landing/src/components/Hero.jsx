// import React, { useState } from "react";
// import { Icons } from "../assets/images";
// import { motion } from "framer-motion";

// const Hero = () => {
//   return (
//     <div className="relative w-full min-h-[700px] md:h-[600px] bg-white overflow-hidden flex flex-col ">
//       {/* Background radial gradients */}
//       <motion.div
//         initial={{ opacity: 0, y: 120 }}
//         animate={{ opacity: 1, y: 0 }}
//         transition={{ duration: 0.6, delay: 1 }}
//         className="absolute top-[35%] left-[-5%] w-[600px] h-[600px]  bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] rounded-full blur-[140px] opacity-80"
//       ></motion.div>
//       <motion.div
//         initial={{ opacity: 0, y: 120 }}
//         animate={{ opacity: 1, y: 0 }}
//         transition={{ duration: 0.6, delay: 1 }}
//         className="absolute top-[35%] right-[-5%] w-[600px] h-[600px] bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] rounded-full blur-[140px] opacity-80"
//       ></motion.div>

//       {/* Navigation */}
//       <motion.nav
//         initial={{ y: -80, opacity: 0 }}
//         animate={{ y: 0, opacity: 1 }}
//         transition={{ duration: 0.6, ease: "easeOut" }}
//         className="relative z-50 flex items-start justify-between w-full max-w-[1440px] mx-auto px-6 py-6"
//       >
//         <div className="flex items-center justify-center w-full md:w-auto">
//           <img src={Icons.logo} alt="Hairlync Logo" />
//         </div>

//         <div className="hidden md:flex items-center gap-3">
//           <div className="flex w-[250px] items-center bg-gradient-to-b from-[#4B8CFF]/20 to-[#ADCBFF]/10 rounded border border-black/10 shadow-sm backdrop-blur-sm py-1.5">
//             <div className="flex items-center pl-2 pr-2 text-gray-500">
//               <svg
//                 width="18"
//                 height="18"
//                 viewBox="0 0 24 24"
//                 fill="none"
//                 stroke="currentColor"
//                 strokeWidth="2"
//               >
//                 <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9-2-2-2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
//                 <polyline points="22,6 12,13 2,6"></polyline>
//               </svg>
//               <input
//                 type="email"
//                 placeholder="Enter your mail..."
//                 className="w-full bg-transparent border-none outline-none text-[15px] font-medium text-gray-700 ml-2 placeholder:text-[#5C5C5C]"
//               />
//             </div>
//           </div>

//           <button className="button-gradient">Get Download link</button>
//         </div>
//       </motion.nav>

//       {/* Main Content Center */}
//       <motion.main
//         initial={{ opacity: 0, y: 60 }}
//         animate={{ opacity: 1, y: 0 }}
//         transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
//         className="relative z-40 flex flex-col items-center w-full max-w-[1440px] mx-auto px-4 pt-12 md:pt-16"
//       >
//         <div className="text-center">
//           <motion.h1
//             initial={{ opacity: 0, y: 40 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.7, delay: 0.3 }}
//             className="text-[44px] md:text-[64px] font-bold text-[#333] leading-[1.05] tracking-tight mb-5 drop-shadow-sm font-PlusJakartaSans"
//           >
//             AI That Finds
//             <br />
//             Your{" "}
//             <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#6b9cfb] to-[#4b84f6]">
//               Perfect
//               <br />
//               Hairstyle
//             </span>
//           </motion.h1>

//           <motion.p
//             initial={{ opacity: 0, y: 30 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.7, delay: 0.5 }}
//             className=" md:text-xl text-[#383838] mb-8 max-[460px] text-center  font-medium leading-relaxed"
//           >
//             Analyze face shape, match hair color <br /> and book your stylist
//             powered by AI.
//           </motion.p>

//           <motion.button
//             initial={{ opacity: 0, y: 30 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.7, delay: 0.7 }}
//             className="bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] text-[#383838] font-medium text-[16px] py-[10px] px-6 md:px-16 lg:px-28 rounded-[8px]  cursor-pointer mb-4 hover:scale-105 transition-all duration-300 ease-in-out"
//           >
//             Start Your Free Trial
//           </motion.button>

//           <motion.div
//             initial={{ opacity: 0, y: 20 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.6, delay: 0.9 }}
//             className="flex items-center justify-center gap-4"
//           >
//             <img
//               src={Icons.google_play}
//               className="h-[46px] cursor-pointer hover:opacity-80 transition-all hover:scale-105 "
//             />
//             <img
//               src={Icons.app_store}
//               className="h-[46px] cursor-pointer hover:opacity-80 transition-all hover:scale-105 "
//             />
//           </motion.div>
//         </div>
//       </motion.main>

//       {/* Desktop */}
//       <div className="w-full absolute bottom-0 left-0 right-0 h-[65%] pointer-events-none hidden md:flex items-end justify-between px-10 lg:px-20">
//         {/* MALE */}
//         <div className="relative w-[800px] h-full pointer-events-auto flex items-end justify-center cursor-pointer group pb-0">
//           <motion.div
//             initial={{ opacity: 0, y: 120 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.6, delay: 0.9 }}
//             className="relative"
//           >
//             <img
//               src={Icons.male}
//               className="w-full max-w-[800px]  object-contain object-bottom relative z-10 cursor-pointer"
//             />

//             <motion.div
//               initial={{ opacity: 0, x: -120 }}
//               animate={{ opacity: 1, x: 0 }}
//               transition={{ duration: 0.6, delay: 2 }}
//               className={`hidden md:block absolute top-[15%] left-[0%] bg-white/20 backdrop-blur-xl shadow-[0_8px_32px_rgba(31,38,135,0.2)]  border border-white/30  rounded-lg p-4 transition-all duration-300 w-48 text-sm text-[#383838]
//               `}
//             >
//               <h3 className="font-bold text-[#383838] mb-2 text-sm">
//                 Live Face Scan
//               </h3>
//               <div className="text-xs text-[#64748b] space-y-1 font-medium">
//                 <p>Analyze Your Shape</p>
//                 <p>Analyze Your Style</p>
//               </div>
//             </motion.div>
//           </motion.div>
//         </div>

//         {/* FEMALE */}
//         <div className="relative w-[800px] h-full pointer-events-auto flex items-end justify-center cursor-pointer group pb-0">
//           <motion.div
//             initial={{ opacity: 0, y: 120 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.9, delay: 0.9 }}
//             className="relative"
//           >
//             <img
//               src={Icons.female}
//               className="w-full max-w-[800px] object-contain object-bottom relative z-10 cursor-pointer"
//             />

//             <motion.div
//               initial={{ opacity: 0, x: 120 }}
//               animate={{ opacity: 1, x: 0 }}
//               transition={{ duration: 0.6, delay: 0.9 }}
//               className={`absolute top-[15%] right-[0%] bg-white/20 backdrop-blur-xl shadow-[0_8px_32px_rgba(31,38,135,0.2)]  border border-white/30  rounded-lg p-4 transition-all duration-300 w-48 text-sm text-[#383838]
//               `}
//             >
//               <p>Analyze With AI</p>
//             </motion.div>

//             <motion.div
//               initial={{ opacity: 0, x: 120 }}
//               animate={{ opacity: 1, x: 0 }}
//               transition={{ duration: 0.6, delay: 0.9 }}
//               className="absolute top-[-5%] right-[12%]
//   bg-white/20
//   backdrop-blur-xl
//   border border-white/30
//   shadow-[0_8px_32px_rgba(31,38,135,0.2)]
//   rounded-lg
//   px-5 py-4
//   text-[#383838] rotate-[-6deg]
//   "
//             >
//               <p className="text-sm tracking-wide">Analyze & Recommend</p>
//             </motion.div>
//           </motion.div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Hero;

// with text animation

import React, { useEffect, useState } from "react";
import { Icons } from "../assets/images";
import { motion } from "framer-motion";

const Hero = () => {
  const fullText = "Perfect Hairstyle";
  const [displayText, setDisplayText] = useState("");
  const [index, setIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const speed = isDeleting ? 80 : 120;

    const timeout = setTimeout(() => {
      if (!isDeleting) {
        setDisplayText(fullText.substring(0, index + 1));
        setIndex(index + 1);

        if (index + 1 === fullText.length) {
          setTimeout(() => setIsDeleting(true), 1000);
        }
      } else {
        setDisplayText(fullText.substring(0, index - 1));
        setIndex(index - 1);

        if (index - 1 === 0) {
          setIsDeleting(false);
        }
      }
    }, speed);

    return () => clearTimeout(timeout);
  }, [index, isDeleting]);

  //   face scanning animation

  return (
    <div className="relative w-full min-h-[700px] md:h-[600px] bg-white overflow-hidden flex flex-col ">
      {/* Background radial gradients */}
      <motion.div
        initial={{ opacity: 0, y: 120 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1 }}
        className="absolute top-[35%] left-[-5%] w-[600px] h-[600px]  bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] rounded-full blur-[140px] opacity-80"
      ></motion.div>
      <motion.div
        initial={{ opacity: 0, y: 120 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1 }}
        className="absolute top-[35%] right-[-5%] w-[600px] h-[600px] bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] rounded-full blur-[140px] opacity-80"
      ></motion.div>

      {/* Navigation */}
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-50 flex items-start justify-between w-full max-w-[1440px] mx-auto px-6 py-6"
      >
        <div className="flex items-center justify-center w-full md:w-auto">
          <img src={Icons.logo} alt="Hairlync Logo" />
        </div>

        <div className="hidden md:flex items-center gap-3">
          <div className="flex w-[250px] items-center bg-gradient-to-b from-[#4B8CFF]/20 to-[#ADCBFF]/10 rounded border border-black/10 shadow-sm backdrop-blur-sm py-1.5">
            <div className="flex items-center pl-2 pr-2 text-gray-500">
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9-2-2-2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
              </svg>
              <input
                type="email"
                placeholder="Enter your mail..."
                className="w-full bg-transparent border-none outline-none text-[15px] font-medium text-gray-700 ml-2 placeholder:text-[#5C5C5C]"
              />
            </div>
          </div>

          <button className="button-gradient">Get Download link</button>
        </div>
      </motion.nav>

      {/* Main Content Center */}
      <motion.main
        initial={{ opacity: 0, y: 60 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
        className="relative z-40 flex flex-col items-center w-full max-w-[1440px] mx-auto px-4 pt-12 md:pt-16"
      >
        <div className="text-center">
          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="text-[44px] md:text-[64px] font-bold text-[#333] leading-[1.05] tracking-tight mb-5 drop-shadow-sm font-PlusJakartaSans"
          >
            AI That Finds
            <br />
            Your{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#6b9cfb] to-[#4b84f6]">
              {displayText.includes(" ") ? (
                <>
                  {displayText.split(" ")[0]} <br />
                  {displayText.split(" ")[1]}
                </>
              ) : (
                displayText
              )}
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5 }}
            className=" md:text-xl text-[#383838] mb-8 max-[460px] text-center  font-medium leading-relaxed"
          >
            Analyze face shape, match hair color <br /> and book your stylist
            powered by AI.
          </motion.p>

          <motion.button
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.7 }}
            className="bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] text-[#383838] font-medium text-[16px] py-[10px] px-6 md:px-16 lg:px-28 rounded-[8px]  cursor-pointer mb-4 hover:scale-105 transition-all duration-300 ease-in-out"
          >
            Start Your Free Trial
          </motion.button>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.9 }}
            className="flex items-center justify-center gap-4"
          >
            <img
              src={Icons.google_play}
              className="h-[46px] cursor-pointer hover:opacity-80 transition-all hover:scale-105 "
            />
            <img
              src={Icons.app_store}
              className="h-[46px] cursor-pointer hover:opacity-80 transition-all hover:scale-105 "
            />
          </motion.div>
        </div>
      </motion.main>

      {/* Desktop */}
      <div className="w-full absolute bottom-0 left-0 right-0 h-[65%] pointer-events-none hidden md:flex items-end justify-between px-10 lg:px-20">
        {/* MALE */}
        <div className="relative w-[800px] h-full pointer-events-auto flex items-end justify-center cursor-pointer group pb-0">
          <motion.div
            initial={{ opacity: 0, y: 120 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.9 }}
            className="relative"
          >
            <img
              src={Icons.male}
              className="w-full max-w-[800px]  object-contain object-bottom relative z-10 cursor-pointer"
            />

            <motion.div
              initial={{ opacity: 0, x: -120 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 2 }}
              className={`hidden md:block absolute top-[15%] left-[0%] bg-white/20 backdrop-blur-xl shadow-[0_8px_32px_rgba(31,38,135,0.2)]  border border-white/30  rounded-lg p-4 transition-all duration-300 w-48 text-sm text-[#383838]
              `}
            >
              <h3 className="font-bold text-[#383838] mb-2 text-sm">
                Live Face Scan
              </h3>
              <div className="text-xs text-[#64748b] space-y-1 font-medium">
                <p>Analyze Your Shape</p>
                <p>Analyze Your Style</p>
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* FEMALE */}
        <div className="relative w-[800px] h-full pointer-events-auto flex items-end justify-center cursor-pointer group pb-0">
          <motion.div
            initial={{ opacity: 0, y: 120 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.9 }}
            className="relative"
          >
            <img
              src={Icons.female}
              className="w-full max-w-[800px] object-contain object-bottom relative z-10 cursor-pointer"
            />

            <motion.div
              initial={{ opacity: 0, x: 120 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.9 }}
              className={`absolute top-[15%] right-[0%] bg-white/20 backdrop-blur-xl shadow-[0_8px_32px_rgba(31,38,135,0.2)]  border border-white/30  rounded-lg p-4 transition-all duration-300 w-48 text-sm text-[#383838]
              `}
            >
              <p>Analyze With AI</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 120 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.9 }}
              className="absolute top-[-5%] right-[12%]
  bg-white/20
  backdrop-blur-xl
  border border-white/30
  shadow-[0_8px_32px_rgba(31,38,135,0.2)]
  rounded-lg
  px-5 py-4
  text-[#383838] rotate-[-6deg]
  "
            >
              <p className="text-sm tracking-wide">Analyze & Recommend</p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
