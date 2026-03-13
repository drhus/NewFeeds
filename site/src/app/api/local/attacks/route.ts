import { NextResponse } from "next/server";
import path from "path";
import fs from "fs";


const FILE = path.resolve(process.cwd(), "../data/attacks.json");

export async function GET() {
  try {
    const raw = fs.readFileSync(FILE, "utf-8");
    return NextResponse.json(JSON.parse(raw));
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
