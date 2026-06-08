// import React from "react";
// import { Icons } from "../assets/images";

// const Mission = () => {
//   return (
//     <section className="relative w-full min-h-[850px] bg-white flex flex-col items-center overflow-hidden pt-16 md:pt-28 pb-0">
//       {/* Background Radial Glow */}
//       <div className="absolute bottom-[10%] left-[-10%] w-[600px] h-[600px] bg-[#6b8cfa] opacity-[0.15] blur-[150px] rounded-full pointer-events-none z-0"></div>
//       <div className="absolute top-[30%] right-[-5%] w-[500px] h-[500px] bg-[#6b8cfa] opacity-[0.15] blur-[140px] rounded-full pointer-events-none z-0"></div>

//       <div className="w-full max-w-7xl mx-auto px-4 relative z-10 flex flex-col items-center justify-start h-full">
//         {/* Header Content */}
//         <div className="text-center max-w-4xl flex flex-col items-center z-30 mb-10">
//           <h3 className="text-[22px] md:text-[28px] font-bold text-[#333] mb-4">
//             Our Mission
//           </h3>
//           <h2 className="text-[32px] md:text-[54px] font-bold bg-clip-text text-transparent bg-[#76a0fa] mb-6 leading-[1.2] tracking-tight">
//             To Connect the World Through
//             <br className="hidden md:block" /> Personalized Style Discovery
//           </h2>
//           <p className="text-[#64748b] text-[15px] md:text-[18px] mb-8 max-w-[600px] font-medium leading-relaxed">
//             Find a plan that helps you discover new styles and connect with
//             <br className="hidden sm:block" /> top stylists.
//           </p>

//           <div className="flex items-center justify-center gap-4 mb-6">
//             <a
//               href="#"
//               className="hover:opacity-80 transition-opacity transform hover:scale-105 duration-300"
//             >
//               <img
//                 src={Icons.google_play}
//                 alt="Google Play"
//                 className="h-[42px] md:h-[48px] object-contain"
//               />
//             </a>
//             <a
//               href="#"
//               className="hover:opacity-80 transition-opacity transform hover:scale-105 duration-300"
//             >
//               <img
//                 src={Icons.app_store}
//                 alt="App Store"
//                 className="h-[42px] md:h-[48px] object-contain"
//               />
//             </a>
//           </div>

//           <button className="bg-gradient-to-r from-[#709bf9] to-[#71a5fc] hover:from-[#5b8df7] hover:to-[#5ea0fc] text-white font-semibold text-[16px] py-[14px] px-32 rounded-[8px] shadow-[0_10px_25px_rgba(112,155,249,0.3)] transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
//             Download the App
//           </button>
//         </div>
//       </div>

//       {/* Floating Hands Output (Desktop & Large Screens) */}
//       <div className="hidden lg:block absolute bottom-0 left-0 right-0 w-full h-[600px] pointer-events-none z-20">
//         {/* Left Hand Image */}
//         <img
//           src={Icons.L_phone}
//           alt="App screen left hand"
//           className="absolute left-[-5%] bottom-[-8%] w-[45%] max-w-[640px] h-auto object-contain transform origin-bottom-left hover:rotate-2 hover:scale-[1.02] transition-all duration-700 ease-out pointer-events-auto"
//         />

//         {/* Right Hand Image */}
//         <img
//           src={Icons.R_phone}
//           alt="App screen right hand"
//           className="absolute right-[-4%] bottom-[5%] w-[42%] max-w-[600px] h-auto object-contain transform origin-bottom-right hover:-rotate-2 hover:scale-[1.02] transition-all duration-700 ease-out pointer-events-auto drop-shadow-2xl"
//         />
//       </div>

//       {/* iPad / Medium Screen specific layout */}
//       <div className="hidden md:flex lg:hidden absolute bottom-0 left-0 w-full justify-between items-end overflow-hidden z-20 pointer-events-none h-[450px]">
//         <img
//           src={Icons.L_phone}
//           alt="App screen left hand"
//           className="w-[50%] h-auto object-cover transform translate-y-10"
//         />
//         <img
//           src={Icons.R_phone}
//           alt="App screen right hand"
//           className="w-[50%] h-auto object-cover transform translate-y-10"
//         />
//       </div>

//       {/* Mobile Version Hands (Static stacking) */}
//       <div className="md:hidden w-full flex flex-col items-center mt-12 space-y-6 px-4 z-20 relative pb-10">
//         <img
//           src={Icons.L_phone}
//           alt="App screen left hand"
//           className="w-full max-w-[320px] h-auto drop-shadow-xl"
//         />
//         <img
//           src={Icons.R_phone}
//           alt="App screen right hand"
//           className="w-full max-w-[320px] h-auto drop-shadow-xl"
//         />
//       </div>
//     </section>
//   );
// };

// export default Mission;


// update code 

import React from "react";
import { Icons } from "../assets/images";

const Mission = () => {
  return (
    <section className="relative w-full min-h-[1050px] bg-white flex flex-col items-center overflow-hidden pt-16 md:pt-28 pb-0">
      {/* Background Radial Glow */}
      
      <div className="absolute bottom-[10%] left-[-10%] w-[550px] h-[350px] bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF] opacity-[0.90] blur-[110px] rounded-full pointer-events-none z-0"></div>
  
      <div className="absolute bottom-[10%] right-[-10%] w-[500px] h-[300px] bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF] opacity-[0.90] blur-[110px] rounded-full pointer-events-none z-0"></div>

      <div className="w-full max-w-7xl mx-auto px-4 relative z-10 flex flex-col items-center justify-start h-full">
        {/* Header Content */}
        <div className="text-center max-w-4xl flex flex-col items-center z-30 mb-10">
          <h3 className="text-[22px] md:text-[38px] font-semibold text-[#383838] mb-4 font-PlusJakartaSans">
            Our Mission
          </h3>
          <h2 className="text-[32px] md:text-[54px] font-bold  mb-6 leading-[1.2] tracking-tight bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF]/50 
  bg-clip-text text-transparent  ">
            To Connect the World Through
            <br className="hidden md:block" /> Personalized Style Discovery
          </h2>
          <p className="text-[#64748b] text-[15px] md:text-[18px] mb-8 max-w-[600px] font-medium leading-relaxed">
            Find a plan that helps you discover new styles and connect with
            <br className="hidden sm:block" /> top stylists.
          </p>

          <div className="flex items-center justify-center gap-4 mb-6">
            <a
              href="#"
              className="hover:opacity-80 transition-opacity transform hover:scale-105 duration-300"
            >
              <img
                src={Icons.google_play}
                alt="Google Play"
                className="h-[42px] md:h-[48px] object-contain"
              />
            </a>
            <a
              href="#"
              className="hover:opacity-80 transition-opacity transform hover:scale-105 duration-300"
            >
              <img
                src={Icons.app_store}
                alt="App Store"
                className="h-[42px] md:h-[48px] object-contain"
              />
            </a>
          </div>

          <button className="bg-gradient-to-r from-[#709bf9] to-[#71a5fc] hover:from-[#5b8df7] hover:to-[#5ea0fc] text-white font-semibold text-[16px] py-[14px] px-6 md:px-16 lg:px-32 rounded-[8px] shadow-[0_10px_25px_rgba(112,155,249,0.3)] transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
            Download the App
          </button>
        </div>
      </div>

      {/* Floating Hands Output (Desktop & Large Screens) */}
      <div className="hidden lg:block absolute bottom-0 left-0 right-0 w-full h-[600px] pointer-events-none z-20">
        {/* Left Hand Image */}
        <img
          src={Icons.L_phone}
          alt="App screen left hand"
          className="absolute left-[-5%] bottom-[-8%] w-[45%] max-w-[640px] h-auto object-contain transform origin-bottom-left hover:rotate-2 hover:scale-[1.02] transition-all duration-700 ease-out pointer-events-auto"
        />

        {/* Right Hand Image */}
        <img
          src={Icons.R_phone}
          alt="App screen right hand"
          className="absolute right-[-4%] bottom-[5%] w-[42%] max-w-[600px] h-auto object-contain transform origin-bottom-right hover:-rotate-2 hover:scale-[1.02] transition-all duration-700 ease-out pointer-events-auto drop-shadow-2xl"
        />
      </div>

      {/* iPad / Medium Screen specific layout */}
      <div className="hidden md:flex lg:hidden absolute -bottom-0 left-0 w-full justify-between items-end overflow-hidden z-20 pointer-events-none h-[450px]">
        <img
          src={Icons.L_phone}
          alt="App screen left hand"
          className="w-[50%] h-auto object-cover transform translate-y-10"
        />
        <img
          src={Icons.R_phone}
          alt="App screen right hand"
          className="w-[50%] h-auto object-cover transform translate-y-10"
        />
      </div>

      {/* Mobile Version Hands (Static stacking) */}
      <div className="md:hidden w-full flex flex-col items-center mt-12 space-y-6 px-4 z-20 relative pb-10">
        <img
          src={Icons.L_phone}
          alt="App screen left hand"
          className="w-full max-w-[320px] h-auto drop-shadow-xl ml-[-70px]"
        />
        <img
          src={Icons.R_phone}
          alt="App screen right hand"
          className="w-full max-w-[320px] h-auto drop-shadow-xl mr-[-70px]"
        />
      </div>
    </section>
  );
};

export default Mission;


// update code with framer motion 

