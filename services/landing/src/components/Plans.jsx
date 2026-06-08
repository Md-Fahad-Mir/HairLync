// import React from "react";
// import { motion } from "framer-motion";
// import { Icons } from "../assets/images";

// const CheckIcon = () => (
//   <svg
//     width="18"
//     height="18"
//     viewBox="0 0 24 24"
//     fill="none"
//     xmlns="http://www.w3.org/2000/svg"
//     className="mr-3 flex-shrink-0"
//   >
//     <circle cx="12" cy="12" r="10" fill="white" fillOpacity="0.25" />
//     <path
//       d="M16.5 8.5L10.5 14.5L7.5 11.5"
//       stroke="white"
//       strokeWidth="2"
//       strokeLinecap="round"
//       strokeLinejoin="round"
//     />
//   </svg>
// );

// // Animation Variants
// const container = {
//   hidden: {},
//   show: {
//     transition: {
//       staggerChildren: 0.25,
//     },
//   },
// };

// const cardVariant = {
//   hidden: {
//     opacity: 0,
//     y: 60,
//     scale: 0.95,
//     filter: "blur(10px)",
//   },
//   show: {
//     opacity: 1,
//     y: 0,
//     scale: 1,
//     filter: "blur(0px)",
//     transition: {
//       duration: 0.7,
//       ease: "easeOut",
//     },
//   },
// };

// const textVariant = {
//   hidden: {
//     opacity: 0,
//     y: 30,
//     filter: "blur(6px)",
//   },
//   show: {
//     opacity: 1,
//     y: 0,
//     filter: "blur(0px)",
//     transition: {
//       duration: 0.6,
//     },
//   },
// };

// const itemVariant = {
//   hidden: { opacity: 0, x: -20 },
//   show: (i) => ({
//     opacity: 1,
//     x: 0,
//     transition: {
//       delay: i * 0.1,
//     },
//   }),
// };

// const Plans = () => {
//   return (
//     <section className="w-full  pb-32 bg-white flex flex-col items-center overflow-hidden relative">
//       {/* Background radial glow */}
//       {/* <motion.div
//         initial={{ opacity: 0 }}
//         animate={{ opacity: 0.15 }}
//         transition={{ duration: 1.2 }}
//         className="absolute top-[30%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#6b8cfa] blur-[120px] rounded-full pointer-events-none z-0"
//       /> */}

//       <div className="w-full max-w-[1440px] mx-auto px-4 md:px-8 relative z-10">
//         {/* Header */}
//         <motion.div
//           variants={textVariant}
//           initial="hidden"
//           whileInView="show"
//           viewport={{ once: true }}
//           className="text-center mb-16 md:mb-20"
//         >
//           <h2 className="text-4xl md:text-[50px] font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#6b8cfa] to-[#4068f5] mb-5 tracking-tight inline-block">
//             Choose The Right Plan For You
//           </h2>
//           <p className="text-[#64748b] text-[16px] md:text-[18px] font-medium">
//             Flexible plans to match your needs.
//           </p>
//         </motion.div>

//         {/* Cards */}
//         <motion.div
//           variants={container}
//           initial="hidden"
//           whileInView="show"
//           viewport={{ once: true }}
//           className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 max-w-5xl mx-auto items-center"
//         >
//           {/* Card 1 */}
//           <motion.div
//             variants={cardVariant}
//             className="rounded-[28px] p-4 md:p-6 bg-gradient-to-br from-[#a6c1fb] to-[#92aef3] text-white flex flex-col shadow-sm border border-white/50 transform hover:-translate-y-2 hover:shadow-xl transition-all duration-300 md:h-[420px]"
//           >
//             <h3 className="text-[19px] font-medium mb-3 text-white/90">Free</h3>

//             <div className="flex items-baseline mb-4">
//               <span className="text-[52px] font-bold tracking-tighter">$0</span>
//               <span className="text-white/80 ml-2 text-[15px] font-medium">
//                 /month
//               </span>
//             </div>

//             <p className="text-[14px] text-white/90 mb-4 min-h-[44px] leading-relaxed">
//               Discover your next look with confidence.
//             </p>

//             <ul className="space-y-3 flex-grow mb-2">
//               {[
//                 "Search top stylists & barbers near you",
//                 "View portfolios & reviews",
//                 "Book appointments instantly",
//                 "Save your favorite looks",
//               ].map((item, i) => (
//                 <motion.li
//                   key={i}
//                   custom={i}
//                   variants={itemVariant}
//                   className="flex items-start text-[15px] font-medium text-white/95"
//                 >
//                   <CheckIcon /> {item}
//                 </motion.li>
//               ))}
//             </ul>
//           </motion.div>

//           {/* Card 2 */}
//           <motion.div
//             variants={cardVariant}
//             className="rounded-[28px] p-4 md:p-6 bg-gradient-to-br from-[#6292fb] to-[#4f83f6] text-white flex flex-col shadow-[0_20px_50px_rgba(98,146,251,0.25)] border border-white/20 transform hover:-translate-y-2 hover:shadow-[0_20px_50px_rgba(98,146,251,0.4)] transition-all duration-300 relative z-20 md:scale-[1.05] md:h-[450px]"
//           >
//             {/* <div className="absolute top-[10%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-[363px] h-[418px] bg-[#6b8cfa] opacity-15 blur-[120px] rounded-full pointer-events-none z-0"></div> */}

//             <h3 className="text-[19px] font-medium mb-3 text-white/90">
//               Pro Monthly
//             </h3>

//             <div className="flex items-baseline mb-2">
//               <span className="text-[52px] font-bold tracking-tighter">
//                 $25
//               </span>
//               <span className="text-white/80 ml-2 text-[15px] font-medium">
//                 /month
//               </span>
//             </div>

//             <p className="text-[14px] text-white/90  min-h-[44px] leading-relaxed">
//               Stand out and sharpen your craft.
//             </p>

//             <ul className="space-y-3 flex-grow mb-2">
//               {[
//                 "AI face scan for personalized style previews",
//                 "Step-by-step haircut & styling tutorials",
//                 "Integrated learning via YouTube",
//                 "Booking & client management tools",
//                 "Showcase your work & build reviews",
//               ].map((item, i) => (
//                 <motion.li
//                   key={i}
//                   custom={i}
//                   variants={itemVariant}
//                   className="flex items-start text-[15px] font-medium text-white/95"
//                 >
//                   <CheckIcon /> {item}
//                 </motion.li>
//               ))}
//             </ul>
//           </motion.div>

//           {/* Card 3 */}
//           <motion.div
//             variants={cardVariant}
//             className="rounded-[28px] p-4 md:p-6 bg-gradient-to-br from-[#2f67e5] to-[#1447ba] text-white flex flex-col shadow-sm border border-white/10 transform hover:-translate-y-2 hover:shadow-xl transition-all duration-300 md:h-[420px]"
//           >
//             <h3 className="text-[19px] font-medium mb-3 text-white/90">
//               Pro Annual
//             </h3>

//             <div className="flex items-baseline mb-2">
//               <span className="text-[52px] font-bold tracking-tighter">
//                 $75
//               </span>
//               <span className="text-white/80 ml-2 text-[15px] font-medium">
//                 /year
//               </span>
//             </div>

//             <p className="text-[14px] text-white/90 mb-8 min-h-[44px] leading-relaxed">
//               Run your shop like a modern brand.
//             </p>

//             <ul className="space-y-3 flex-grow mb-2">
//               {[
//                 "Everything in Independent",
//                 "Up to 10 stylist profiles",
//                 "Team scheduling & management",
//                 "AI-powered client experience",
//                 "Business growth insights",
//               ].map((item, i) => (
//                 <motion.li
//                   key={i}
//                   custom={i}
//                   variants={itemVariant}
//                   className="flex items-center text-[15px] font-medium text-white/95"
//                 >
//                   <CheckIcon /> {item}
//                 </motion.li>
//               ))}
//             </ul>
//           </motion.div>
//         </motion.div>
//       </div>
//     </section>
//   );
// };

// export default Plans;

import React from "react";
import { motion } from "framer-motion";

const CheckIcon = () => (
  <svg
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className="mr-3 flex-shrink-0"
  >
    <circle cx="12" cy="12" r="10" fill="white" fillOpacity="0.25" />
    <path
      d="M16.5 8.5L10.5 14.5L7.5 11.5"
      stroke="white"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

// Animation Variants
const container = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.25,
    },
  },
};

const cardVariant = {
  hidden: {
    opacity: 0,
    y: 60,
    scale: 0.95,
    filter: "blur(10px)",
  },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    filter: "blur(0px)",
    transition: {
      duration: 0.7,
      ease: "easeOut",
    },
  },
};

const textVariant = {
  hidden: {
    opacity: 0,
    y: 30,
    filter: "blur(6px)",
  },
  show: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: {
      duration: 0.6,
    },
  },
};

const itemVariant = {
  hidden: { opacity: 0, x: -20 },
  show: (i) => ({
    opacity: 1,
    x: 0,
    transition: {
      delay: i * 0.1,
    },
  }),
};

const Plans = () => {
  return (
    <section className="w-full pb-32 bg-white flex flex-col items-center overflow-hidden relative">
      <div className="w-full max-w-[1440px] mx-auto px-4 md:px-8 relative z-10">
        {/* Header */}
        <motion.div
          variants={textVariant}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="text-center mb-16 md:mb-20"
        >
          <h2 className="text-4xl md:text-[50px] font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#6b8cfa] to-[#4068f5] mb-5 tracking-tight inline-block">
            Choose The Right Plan For You
          </h2>
          <p className="text-[#64748b] text-[16px] md:text-[18px] font-medium">
            Flexible plans to match your needs.
          </p>
        </motion.div>

        {/* Cards */}
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 max-w-5xl mx-auto items-center"
        >
          {/* Card 1 */}
          <motion.div
            variants={cardVariant}
            className="rounded-[28px] p-4 md:p-6 bg-gradient-to-br from-[#a6c1fb] to-[#92aef3] text-white flex flex-col shadow-sm border border-white/50 transform hover:-translate-y-2 hover:shadow-xl transition-all duration-300 "
          >
            <h3 className="text-[19px] font-medium mb-3 text-white/90">
              Free Plan
            </h3>

            <div className="flex items-baseline mb-4">
              <span className="text-[52px] font-bold tracking-tighter">$0</span>
              <span className="text-white/80 ml-2 text-[15px] font-medium">
                /month
              </span>
            </div>

            <p className="text-[14px] text-white/90 mb-4 min-h-[44px] leading-relaxed">
              Discover your next look with confidence.
            </p>

            <ul className="space-y-3 flex-grow mb-2">
              {[
                "Search top stylists & barbers near you",
                "View portfolios & reviews",
                "Book appointments instantly",
                "Save your favorite looks",
              ].map((item, i) => (
                <motion.li
                  key={i}
                  custom={i}
                  variants={itemVariant}
                  className="flex items-start text-[15px] font-medium text-white/95"
                >
                  <CheckIcon /> {item}
                </motion.li>
              ))}
            </ul>

            <button className="mt-4 w-full py-3 rounded-lg bg-white text-[#4f83f6] font-semibold cursor-pointer">
              Get Started Free
            </button>
          </motion.div>

          {/* Card 2 */}
          <motion.div
            variants={cardVariant}
            className="rounded-[28px] p-4 md:p-6 bg-gradient-to-br from-[#6292fb] to-[#4f83f6] text-white flex flex-col shadow-[0_20px_50px_rgba(98,146,251,0.25)] border border-white/20 transform hover:-translate-y-2 hover:shadow-[0_20px_50px_rgba(98,146,251,0.4)] transition-all duration-300 relative z-20 md:scale-[1.05] "
          >
            <h3 className="text-[19px] font-medium mb-3 text-white/90">
              Professionals Plan
            </h3>

            <div className="flex items-baseline mb-4">
              <span className="text-[52px] font-bold tracking-tighter">
                $25
              </span>
              <span className="text-white/80 ml-2 text-[15px] font-medium">
                /month
              </span>
            </div>

            <p className="text-[14px] text-white/90 min-h-[44px] mb-4 leading-relaxed">
              Stand out and sharpen your craft.
            </p>

            <ul className="space-y-3 flex-grow mb-2">
              {[
                "AI face scan for personalized style previews",
                "Step-by-step haircut & styling tutorials",
                "Integrated learning via YouTube",
                "Booking & client management tools",
                "Showcase your work & build reviews",
              ].map((item, i) => (
                <motion.li
                  key={i}
                  custom={i}
                  variants={itemVariant}
                  className="flex items-start text-[15px] font-medium text-white/95"
                >
                  <CheckIcon /> {item}
                </motion.li>
              ))}
            </ul>

            <button className="mt-4 w-full py-3 rounded-xl bg-white text-[#4f83f6] font-semibold cursor-pointer">
              Start Growing
            </button>
          </motion.div>

          {/* Card 3 */}
          <motion.div
            variants={cardVariant}
            className="rounded-[28px] p-4 md:p-6 bg-gradient-to-br from-[#2f67e5] to-[#1447ba] text-white flex flex-col shadow-sm border border-white/10 transform hover:-translate-y-2 hover:shadow-xl transition-all duration-300"
          >
            <h3 className="text-[19px] font-medium mb-3 text-white/90">
              Business Plan
            </h3>

            <div className="flex items-baseline mb-4">
              <span className="text-[52px] font-bold tracking-tighter">
                $75
              </span>
              <span className="text-white/80 ml-2 text-[15px] font-medium">
                /month
              </span>
            </div>

            <p className="text-[14px] text-white/90 mb-4 min-h-[44px] leading-relaxed">
              Run your shop like a modern brand.
            </p>

            <ul className="space-y-3 flex-grow mb-2">
              {[
                "Everything in Independent",
                "Up to 10 stylist profiles",
                "Team scheduling & management",
                "AI-powered client experience",
                "Business growth insights",
              ].map((item, i) => (
                <motion.li
                  key={i}
                  custom={i}
                  variants={itemVariant}
                  className="flex items-center text-[15px] font-medium text-white/95"
                >
                  <CheckIcon /> {item}
                </motion.li>
              ))}
            </ul>

            <button className="mt-4 w-full py-3 rounded-xl bg-white text-[#1447ba] font-semibold cursor-pointer">
              Scale Your Shop
            </button>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default Plans;
