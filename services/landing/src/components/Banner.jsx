// import React, { useState } from "react";
// import { Icons } from "../assets/images";

// const Hero = () => {
//   return (
//     <div className="relative w-full min-h-[900px] md:h-[600px] bg-white overflow-hidden flex flex-col ">
//       {/* Background radial gradients for the sky-blue lighting effect */}
//       <div className="absolute top-[35%] left-[-5%] w-[600px] h-[600px]  bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] rounded-full blur-[140px] opacity-80"></div>
//       <div className="absolute top-[35%] right-[-5%] w-[600px] h-[600px] bg-gradient-to-b from-[#a6c8ff] to-[#8aa9e0] rounded-full blur-[140px] opacity-80"></div>

//       {/* Navigation */}
//       <nav className="relative z-50 flex items-start justify-between w-full max-w-[1440px] mx-auto px-6 py-6">
//         {/* Logo area - Center logo on mobile */}
//         <div className="flex items-center justify-center w-full md:w-auto">
//           <img src={Icons.logo} alt="Hairlync Logo" className="" />
//         </div>

//         {/* Top Right Mail/Button */}
//         <div className="hidden md:flex items-center gap-3">
//           {/* Input Box */}
//           <div className="flex w-[250px] items-center bg-gradient-to-b from-[#4B8CFF]/20 to-[#ADCBFF]/10 rounded border border-black/10 shadow-sm backdrop-blur-sm py-1.5">
//             {/* shadow-[0_3px_6px_0_rgba(0,0,0,0.16)] */}
//             <div className="flex items-center pl-2 pr-2 text-gray-500">
//               <svg
//                 width="18"
//                 height="18"
//                 viewBox="0 0 24 24"
//                 fill="none"
//                 stroke="currentColor"
//                 strokeWidth="2"
//                 strokeLinecap="round"
//                 strokeLinejoin="round"
//               >
//                 <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
//                 <polyline points="22,6 12,13 2,6"></polyline>
//               </svg>
//               <input
//                 type="email"
//                 placeholder="Enter your mail..."
//                 className="w-full bg-transparent border-none outline-none text-[15px] font-medium text-gray-700 ml-2 placeholder:text-[#5C5C5C]"
//               />
//             </div>
//           </div>

//           {/* Button */}
//           <button className="button-gradient">Get Download link</button>
//         </div>
//       </nav>

//       {/* Main Content Center */}
//       <main className="relative z-40 flex flex-col items-center w-full max-w-[1440px] mx-auto px-4 pt-12 md:pt-16">
//         <div className="text-center">
//           <h1 className="text-[44px] md:text-[64px] font-bold text-[#333] leading-[1.05] tracking-tight mb-5 drop-shadow-sm font-PlusJakartaSans">
//             AI That Finds
//             <br />
//             Your{" "}
//             <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#6b9cfb] to-[#4b84f6]">
//               Perfect
//               <br />
//               Hairstyle
//             </span>
//           </h1>
//           <p className="text-[17px] md:text-[24px] text-[#383838] mb-8 max-w-xl mx-auto font-medium leading-relaxed">
//             Analyze face shape, match hair color and book your stylist powered
//             by AI.
//           </p>

//           <button className="bg-gradient-to-r from-[#6f9ffb] to-[#5b8df7] hover:from-[#5b8df7] hover:to-[#4b84f6] text-white font-semibold text-[17px] py-4 px-10 rounded-lg shadow-[0_15px_30px_rgba(96,165,250,0.4)] transition-all duration-300 transform hover:-translate-y-1 mb-8 w-full sm:w-auto">
//             Start Your Free Trial
//           </button>

//           {/* App Stores */}
//           <div className="flex items-center justify-center gap-4">
//             <a
//               href="#"
//               className="transform hover:scale-105 transition-transform duration-300"
//             >
//               <img
//                 src={Icons.google_play}
//                 alt="Google Play"
//                 className="h-[46px] object-contain"
//               />
//             </a>
//             <a
//               href="#"
//               className="transform hover:scale-105 transition-transform duration-300"
//             >
//               <img
//                 src={Icons.app_store}
//                 alt="App Store"
//                 className="h-[46px] object-contain"
//               />
//             </a>
//           </div>
//         </div>
//       </main>

//       {/* Floating Interactive Images (Desktop) */}
//       <div className="w-full   absolute bottom-0 left-0 right-0 h-[65%] pointer-events-none hidden md:flex items-end justify-between px-10 lg:px-20">
//         {/* === MALE IMAGE AREA === */}
//         <div
//           className="relative w-[800px] h-full pointer-events-auto flex items-end justify-center cursor-pointer group pb-0"
//         >
//           <div className="relative">
//             <img
//             src={Icons.male}
//             alt="Male model face scan"
//             className={`w-full max-w-[800px] h-auto object-contain object-bottom relative transition-all duration-500 ease-in-out origin-bottom z-10 hover:scale-[1.02]`}
//             style={{
//               maxHeight: "100%",
//               WebkitMaskImage:
//                 "linear-gradient(to top, black 80%, transparent 100%)",
//             }} // Blend at bottom
//           />

//           <div
//             className={`absolute top-[15%] left-[30%] bg-white/80 backdrop-blur shadow-md border border-white/50 rounded-xl p-4 transition-all duration-300 w-48 z-5 `}
//           >
//             <h3 className="font-bold text-[#3d4b60] mb-2 text-sm">
//               Live Face Scan
//             </h3>
//             <div className="text-xs text-[#64748b] space-y-1 font-medium">
//               <p>Analyze Your Shape</p>
//               <p>Analyze Your Style</p>
//             </div>
//           </div>
//           </div>
//         </div>

//         {/* === FEMALE IMAGE AREA === */}
//         <div
//           className="relative w-[800px] h-full pointer-events-auto flex items-end justify-center cursor-pointer group pb-0"
//         >
//           <div className="relative">
//             <img
//             src={Icons.female}
//             alt="Female model face scan"
//             className={`w-full max-w-[800px] h-auto object-contain object-bottom relative transition-all duration-500 ease-in-out origin-bottom z-12 hover:scale-[1.02]`}
//             style={{ maxHeight: "100%" }}
//           />
//           <div>
//             <div className={`absolute top-[15%] right-[20%] bg-white/80 backdrop-blur shadow-md border border-white/50 rounded-xl p-4 transition-all duration-300 w-48 z-8 `}>
//               <p>Analize With AI</p>
//             </div>
//           </div>
//           </div>
//         </div>
//       </div>



//       {/* Floating Interactive Images for Mobile (Static Display) */}
//       <div className="w-full flex md:hidden flex-col items-center space-y-12 pb-10 mt-10 relative z-30">
//         <div
//           className="relative w-[360px] cursor-pointer"
//         >
          
//          <div className="relative">
//            <img
//             src={
//               Icons.male
//             }
//             alt="Male model face scan"
//             className="w-full h-auto object-contain z-10"
//           />

//           <div
//             className={`absolute top-[10%] left-[5%] bg-white/80 backdrop-blur shadow-md border border-white/50 rounded-xl p-4 transition-all duration-300 w-48 -z-5 `}
//           >
//             <h3 className="font-bold text-[#3d4b60] mb-2 text-sm"></h3>
//               Live Face Scan
            
//             <div className="text-xs text-[#64748b] space-y-1 font-medium">
//               <p>Analyze Your Shape</p>
//               <p>Analyze Your Style</p>
//             </div>
//           </div>
//          </div>

//         </div>
//         <div
//           className="relative w-[360px] cursor-pointer"
//         >
          
//          <div className="relative">
//            <img
//             src={
//               Icons.female
//             }
//             alt="Female model face scan"
//             className="w-full h-auto object-contain z-20 "
//           />
//           <div
//             className={`absolute top-[20%] right-[15%] bg-white/80 backdrop-blur shadow-md border border-white/50 rounded-lg p-3 transition-all duration-300 -z-10 `}
//           >
//             <p className="font-bold text-[#3d4b60] text-xs">Analysis With AI</p>
//           </div>
//          </div>
//         </div>

//       </div>
//     </div>
//   );
// };

// export default Hero;

import React, { useState } from "react";
import { Icons } from "../assets/images";

const Hero = () => {
  const [activeCard, setActiveCard] = useState(null);

  return (
    <div
      className="relative w-full min-h-[900px] md:h-[600px] bg-white overflow-hidden flex flex-col "
      onClick={() => setActiveCard(null)}
    >
      {/* Background radial gradients */}
      <div className="absolute top-[35%] left-[-5%] w-[600px] h-[600px]  bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] rounded-full blur-[140px] opacity-80"></div>
      <div className="absolute top-[35%] right-[-5%] w-[600px] h-[600px] bg-gradient-to-b from-[#a6c8ff] to-[#8aa9e0] rounded-full blur-[140px] opacity-80"></div>

      {/* Navigation */}
      <nav className="relative z-50 flex items-start justify-between w-full max-w-[1440px] mx-auto px-6 py-6">
        <div className="flex items-center justify-center w-full md:w-auto">
          <img src={Icons.logo} alt="Hairlync Logo" />
        </div>

        <div className="hidden md:flex items-center gap-3">
          <div className="flex w-[250px] items-center bg-gradient-to-b from-[#4B8CFF]/20 to-[#ADCBFF]/10 rounded border border-black/10 shadow-sm backdrop-blur-sm py-1.5">
            <div className="flex items-center pl-2 pr-2 text-gray-500">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
      </nav>

      {/* Main Content Center */}
      <main className="relative z-40 flex flex-col items-center w-full max-w-[1440px] mx-auto px-4 pt-12 md:pt-16">
        <div className="text-center">
          <h1 className="text-[44px] md:text-[64px] font-bold text-[#333] leading-[1.05] tracking-tight mb-5 drop-shadow-sm font-PlusJakartaSans">
            AI That Finds
            <br />
            Your{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#6b9cfb] to-[#4b84f6]">
              Perfect
              <br />
              Hairstyle
            </span>
          </h1>

          <p className="text-[17px] md:text-[24px] text-[#383838] mb-8 max-w-xl mx-auto font-medium leading-relaxed">
            Analyze face shape, match hair color and book your stylist powered by AI.
          </p>

          <button className="bg-gradient-to-r from-[#6f9ffb] to-[#5b8df7] hover:from-[#5b8df7] hover:to-[#4b84f6] text-white font-semibold text-[17px] py-4 px-10 rounded-lg shadow-[0_15px_30px_rgba(96,165,250,0.4)] transition-all duration-300 transform hover:-translate-y-1 mb-8 w-full sm:w-auto">
            Start Your Free Trial
          </button>

          <div className="flex items-center justify-center gap-4">
            <img src={Icons.google_play} className="h-[46px]" />
            <img src={Icons.app_store} className="h-[46px]" />
          </div>
        </div>
      </main>

      {/* Desktop */}
      <div className="w-full absolute bottom-0 left-0 right-0 h-[65%] pointer-events-none hidden md:flex items-end justify-between px-10 lg:px-20">
        
        {/* MALE */}
        <div
          className="relative w-[800px] h-full pointer-events-auto flex items-end justify-center cursor-pointer group pb-0"
          onClick={(e) => {
            e.stopPropagation();
            setActiveCard(activeCard === "male" ? null : "male");
          }}
        >
          <div className="relative">
            <img
              src={Icons.male}
              className="w-full max-w-[800px] object-contain object-bottom relative z-10 cursor-pointer"
            />

            <div
              className={`absolute top-[15%] left-[30%] bg-white/80 backdrop-blur shadow-md border border-white/50 rounded-xl p-4 transition-all duration-300 w-48
              ${activeCard === "male" ? "z-50 scale-105" : "z-0"}`}
            >
              <h3 className="font-bold text-[#3d4b60] mb-2 text-sm">
                Live Face Scan
              </h3>
              <div className="text-xs text-[#64748b] space-y-1 font-medium">
                <p>Analyze Your Shape</p>
                <p>Analyze Your Style</p>
              </div>
            </div>
          </div>
        </div>

        {/* FEMALE */}
        <div
          className="relative w-[800px] h-full pointer-events-auto flex items-end justify-center cursor-pointer group pb-0"
          onClick={(e) => {
            e.stopPropagation();
            setActiveCard(activeCard === "female" ? null : "female");
          }}
        >
          <div className="relative">
            <img
              src={Icons.female}
              className="w-full max-w-[800px] object-contain object-bottom relative z-10 cursor-pointer"
            />

            <div
              className={`absolute top-[15%] right-[20%] bg-white/80 backdrop-blur shadow-md border border-white/50 rounded-xl p-4 transition-all duration-300 w-48
              ${activeCard === "female" ? "z-50 scale-105" : "z-0"}`}
            >
              <p>Analize With AI</p>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile */}
      <div className="w-full flex md:hidden flex-col items-center space-y-12 pb-10 mt-10 relative z-30">
        
        {/* MALE */}
        <div
          className="relative w-[360px] cursor-pointer"
          onClick={(e) => {
            e.stopPropagation();
            setActiveCard(activeCard === "male" ? null : "male");
          }}
        >
          <div className="relative">
            <img src={Icons.male} className="w-full h-auto object-contain z-10" />

            <div
              className={`absolute top-[10%] left-[5%] bg-white/80 backdrop-blur shadow-md border border-white/50 rounded-xl p-4 transition-all duration-300 w-48
              ${activeCard === "male" ? "z-50 scale-105" : "-z-5"}`}
            >
              Live Face Scan
              <div className="text-xs text-[#64748b] space-y-1 font-medium">
                <p>Analyze Your Shape</p>
                <p>Analyze Your Style</p>
              </div>
            </div>
          </div>
        </div>

        {/* FEMALE */}
        <div
          className="relative w-[360px] cursor-pointer"
          onClick={(e) => {
            e.stopPropagation();
            setActiveCard(activeCard === "female" ? null : "female");
          }}
        >
          <div className="relative">
            <img src={Icons.female} className="w-full h-auto object-contain z-20" />

            <div
              className={`absolute top-[20%] right-[15%] bg-white/80 backdrop-blur shadow-md border border-white/50 rounded-lg p-3 transition-all duration-300
              ${activeCard === "female" ? "z-50 scale-105" : "-z-10"}`}
            >
              <p className="font-bold text-[#3d4b60] text-xs">Analysis With AI</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;



// framer motion 
