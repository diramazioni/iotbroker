import { error, json } from "@sveltejs/kit";
import { prisma, get_wsv_range } from '$lib/prisma';


export async function GET({ url, params }) {

  //const range:BigInt[] = await get_wsv_range(url, params.device)

  return json([])
}