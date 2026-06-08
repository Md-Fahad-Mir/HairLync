import React from "react";
import { motion } from "framer-motion";
import { Icons } from "../assets/images";

const Footer = () => {
  const containerVariants = {
    hidden: { opacity: 0, y: 30 },
    show: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        ease: "easeOut",
      },
    },
  };

  const socialContainerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.4,
      },
    },
  };

  const iconVariants = {
    hidden: { opacity: 0, scale: 0.5, y: 10 },
    show: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: { duration: 0.4, type: "spring", stiffness: 200 },
    },
  };

  return (
    <motion.footer
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.2 }}
      variants={containerVariants}
      className="w-full bg-[#002669] text-white py-12 px-6 md:px-16"
    >
      <div className="max-w-[1440px] mx-auto flex flex-col w-full">
        {/* Top Section */}
        <div className="flex flex-col md:flex-row justify-between items-center md:items-start w-full mb-10">
          {/* Logo Area */}
          <div className="flex flex-col items-center mb-8 md:mb-0">
            <img
              src={Icons.logo}
              alt="Hairlync Logo"
              className="w-[170px] h-auto"
            />
          </div>

          {/* Contact Details */}
          <div className="flex flex-col space-y-4 text-center md:text-left text-white/80 text-[15px] font-medium">
            <p>
              Contact E-mail:{" "}
              <a
                href="mailto:hello@hairlync.com"
                className="hover:text-white transition-colors"
              >
                hello@hairlync.com
              </a>
            </p>
            <p>
              Support E-mail:{" "}
              <a
                href="mailto:support@hairlync.com"
                className="hover:text-white transition-colors"
              >
                support@hairlync.com
              </a>
            </p>
          </div>
        </div>

        {/* Divider */}
        <div className="w-full h-[1px] bg-white/20 mb-6"></div>

        {/* Bottom Section */}
        <div className="flex flex-col md:flex-row justify-between items-center w-full space-y-5 md:space-y-0">
          {/* Copyright */}
          <div className="text-white/50 text-[14px]">
            © 2026 Hairlync, Inc. All rights reserved.
          </div>

          {/* Social Icons */}
          <motion.div
            variants={socialContainerVariants}
            className="flex items-center space-x-5"
          >
            <motion.a
              href="#"
              variants={iconVariants}
              whileHover={{ scale: 1.15 }}
              className="transition-transform duration-300"
            >
              <img
                src={Icons.twitter}
                alt="Twitter"
                className="w-[34px] h-[34px]"
              />
            </motion.a>
            <motion.a
              href="#"
              variants={iconVariants}
              whileHover={{ scale: 1.15 }}
              className="transition-transform duration-300"
            >
              <img
                src={Icons.instagram}
                alt="Instagram"
                className="w-[34px] h-[34px]"
              />
            </motion.a>
            <motion.a
              href="#"
              variants={iconVariants}
              whileHover={{ scale: 1.15 }}
              className="transition-transform duration-300"
            >
              <img
                src={Icons.facebook}
                alt="Facebook"
                className="w-[34px] h-[34px]"
              />
            </motion.a>
          </motion.div>
        </div>
      </div>
    </motion.footer>
  );
};

export default Footer;
