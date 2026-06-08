import React from "react";

const Freetrial = () => {
  return (
    <section className="w-full max-w-[1440px] mx-auto py-20 md:py-32 bg-white flex justify-center items-center">
      <div className="flex flex-col items-center text-center px-4 max-w-4xl w-full">
        {/* <h2 className="text-[36px] md:text-[52px] font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#6b9cfb] to-[#7baeff] mb-5 leading-[1.2] tracking-tight">
          Transform your look with
          <br />a free trial
        </h2> */}
        <h2
          className="text-[36px] md:text-[52px] font-semibold tracking-[1%] 
  bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF]/50 
  bg-clip-text text-transparent 
  mb-5 leading-[55px]"
        >
          Transform your look with
          <br />
          <span
            className="bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF]/50 
  bg-clip-text text-transparent"
          >
            a free trial
          </span>
        </h2>
        <p className="text-[#6B7280] text-[16px] md:text-[18px] font-medium mb-6">
          Start your Hairlync trial for 30 days. No commitment needed.
        </p>
        <button className="bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF]  text-white font-medium text-[16px] md:text-2xl py-[15px] px-16 rounded-[8px]  transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
          Start your free scan
        </button>
      </div>
    </section>
  );
};

export default Freetrial;
