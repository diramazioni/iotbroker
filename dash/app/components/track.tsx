import { Card, Title, Tracker, Flex, Text, Color } from "@tremor/react";

interface Tracker {
    color: Color;
    tooltip: string;
}

const data: Tracker[] = [
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "blue", tooltip: "8 mm" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "blue", tooltip: "10 mm" },
    { color: "blue", tooltip: "22 mm" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Sunny" },
    { color: "yellow", tooltip: "Degraded" },
    { color: "yellow", tooltip: "Sunny" },
];
export default function TrackerCard() {
    return (
        <Card className="max-w-xl mx-auto">
            <Title>Precipitations</Title>
            <Text>Daily water mm drops &bull;</Text>
            <Flex justifyContent="end" className="mt-4">
                <Text>Sunny 92%</Text>
            </Flex>
            <Tracker data={data} className="mt-2" />
        </Card>
    );
}