/*
  Warnings:

  - You are about to drop the column `type` on the `Units` table. All the data in the column will be lost.
  - Added the required column `device_type` to the `Units` table without a default value. This is not possible if the table is not empty.

*/
-- DropIndex
DROP INDEX "Units_name_key";

-- AlterTable
ALTER TABLE "Units" RENAME COLUMN "type" TO "device_type";

-- CreateTable
CREATE TABLE "Messages" (
    "id" SERIAL NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "device_type" TEXT NOT NULL,
    "message" JSONB NOT NULL,

    CONSTRAINT "Messages_pkey" PRIMARY KEY ("id")
);
