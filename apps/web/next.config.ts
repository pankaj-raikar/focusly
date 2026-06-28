import path from "node:path";
import type {NextConfig} from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  turbopack: {
    root: path.join(process.cwd(), "../.."),
  },
};

export default nextConfig;
