// update code with framer motion

import React from "react";
import { motion } from "framer-motion";
import { Icons } from "../assets/images";

const Mission = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: "easeOut" },
    },
  };

  const headingVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.9, ease: "easeOut" },
    },
  };

  const phoneVariants = {
    hidden: { opacity: 0, scale: 0.8, rotate: -10 },
    visible: {
      opacity: 1,
      scale: 1,
      rotate: 0,
      transition: { duration: 1, ease: "easeOut" },
    },
  };

  const floatingAnimation = {
    y: [0, -20, 0],
    transition: {
      duration: 4,
      repeat: Infinity,
      ease: "easeInOut",
    },
  };
  const floatingAnimation_R = {
    y: [0, -7, 0],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  };

  return (
    <section className="relative w-full md:min-h-[1050px] bg-white flex flex-col items-center overflow-hidden pb-0">
      {/* Background Radial Glow */}
      <motion.div
        className="absolute bottom-[10%] left-[-10%] w-[550px] h-[350px] bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF] opacity-[0.90] blur-[110px] rounded-full pointer-events-none z-0"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      ></motion.div>

      <motion.div
        className="absolute bottom-[10%] right-[-10%] w-[500px] h-[300px] bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF] opacity-[0.90] blur-[110px] rounded-full pointer-events-none z-0"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
      ></motion.div>

      <motion.div
        className="w-full max-w-7xl mx-auto px-4 relative z-10 flex flex-col items-center justify-start h-full"
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.3 }}
      >
        {/* Header Content */}
        <div className="text-center max-w-4xl flex flex-col items-center z-30 mb-10">
          <motion.h3
            className="text-[22px] md:text-[38px] font-semibold text-[#383838] mb-4 font-PlusJakartaSans"
            variants={itemVariants}
          >
            Our Mission
          </motion.h3>

          <motion.h2
            className="text-[32px] md:text-[54px] font-bold mb-6 leading-[1.2] tracking-tight bg-gradient-to-r from-[#4B8CFF] to-[#ADCBFF]/50 bg-clip-text text-transparent"
            variants={headingVariants}
          >
            To Connect the World Through
            <br className="hidden md:block" /> Personalized Style Discovery
          </motion.h2>

          <motion.p
            className="text-[#64748b] text-[15px] md:text-[18px] mb-8 max-w-[600px] font-medium leading-relaxed"
            variants={itemVariants}
          >
            Find a plan that helps you discover new styles and connect with
            <br className="hidden sm:block" /> top stylists.
          </motion.p>

          <motion.div
            className="flex items-center justify-center gap-4 mb-6"
            variants={itemVariants}
          >
            <motion.a
              href="#"
              className="hover:opacity-80 transition-opacity"
              whileHover={{ scale: 1.1, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
            >
              <img
                src={Icons.google_play}
                alt="Google Play"
                className="h-[42px] md:h-[48px] object-contain"
              />
            </motion.a>
            <motion.a
              href="#"
              className="hover:opacity-80 transition-opacity"
              whileHover={{ scale: 1.1, rotate: -5 }}
              whileTap={{ scale: 0.95 }}
            >
              <img
                src={Icons.app_store}
                alt="App Store"
                className="h-[42px] md:h-[48px] object-contain"
              />
            </motion.a>
          </motion.div>

          <motion.button
            className="bg-gradient-to-b from-[#4B8CFF] to-[#ADCBFF] text-white font-semibold text-[16px] py-[14px] px-6 md:px-16 lg:px-32 rounded-[8px]  cursor-pointer"
            variants={itemVariants}
            whileHover={{ scale: 1.05, y: -5 }}
            whileTap={{ scale: 0.95 }}
          >
            Download the App
          </motion.button>
        </div>
      </motion.div>

      {/* Floating Hands Output (Desktop & Large Screens) */}
      <div className="hidden lg:block absolute bottom-0 left-0 right-0 w-full h-[600px] pointer-events-none z-20">
        <motion.img
          src={Icons.L_phone}
          alt="App screen left hand"
          className="absolute left-0 bottom-[-6%] w-[45%] max-w-[600px]  2xl:scale-125 h-auto object-contain transform origin-bottom-left pointer-events-auto"
          variants={phoneVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          animate={floatingAnimation}
          // whileHover={{ rotate: 2, scale: 1.05 }}
        />

        <motion.img
          src={Icons.R_phone}
          alt="App screen right hand"
          className="absolute right-0 -bottom-1 w-[45%] max-w-[700px] 2xl:scale-125 h-auto object-contain transform origin-bottom-right pointer-events-auto drop-shadow-2xl"
          variants={phoneVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          animate={floatingAnimation_R}
          // whileHover={{ rotate: -2, scale: 1.05 }}
        />
      </div>

      {/* iPad / Medium Screen specific layout */}
      <div className="hidden md:flex lg:hidden absolute -bottom-0 left-0 w-full justify-between items-end overflow-hidden z-20 pointer-events-none h-[450px]">
        <motion.img
          src={Icons.L_phone}
          alt="App screen left hand"
          className="w-[50%] h-auto object-cover transform translate-y-10"
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          animate={floatingAnimation}
        />
        <motion.img
          src={Icons.R_phone}
          alt="App screen right hand"
          className="w-[50%] h-auto object-cover transform translate-y-10"
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          animate={floatingAnimation}
        />
      </div>

      {/* Mobile Version Hands (Static stacking) */}
      <motion.div
        className="md:hidden w-full flex flex-col items-center mt-12 space-y-6 px-4 z-20 relative pb-10"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <motion.img
          src={Icons.L_phone}
          alt="App screen left hand"
          className="w-full max-w-[320px] h-auto drop-shadow-xl ml-[-70px]"
          initial={{ opacity: 0, y: 30, rotate: -15 }}
          whileInView={{ opacity: 1, y: 0, rotate: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          animate={floatingAnimation}
        />
        <motion.img
          src={Icons.R_phone}
          alt="App screen right hand"
          className="w-full max-w-[320px] h-auto drop-shadow-xl mr-[-70px]"
          initial={{ opacity: 0, y: 30, rotate: 15 }}
          whileInView={{ opacity: 1, y: 0, rotate: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.2 }}
          animate={floatingAnimation}
        />
      </motion.div>
    </section>
  );
};

export default Mission;
