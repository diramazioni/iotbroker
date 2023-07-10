"use client";

import { InformationCircleIcon } from "@heroicons/react/solid";
import { Flex, Title, Icon, TabGroup, TabList, Tab, AreaChart, Text, Color } from "@tremor/react";
import { useState } from "react";

const usNumberformatter = (number: number, decimals = 0) =>
    Intl.NumberFormat("us", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    })
        .format(Number(number))
        .toString();

const formatters: { [key: string]: any } = {
    Temperatures: (number: number) => `${usNumberformatter(number)}&deg;C`,
    Humidity: (number: number) => `${usNumberformatter(number)}%`,
    UV_index: (number: number) => `${usNumberformatter(number)}`,
    Delta: (number: number) => `${usNumberformatter(number, 2)}%`,
};

const Kpis = {
    Temperatures: "Temperatures",
    Humidity: "Humidity",
    UV_index: "UV_index",
};

const kpiList = [Kpis.Temperatures, Kpis.Humidity, Kpis.UV_index];

export type DailyPerformance = {
    date: string;
    Temperatures: number;
    Humidity: number;
    UV_index: number;
};

export const performance: DailyPerformance[] = [
    {
        date: "2023-06-01",
        Temperatures: 17,
        Humidity: 63,
        UV_index: 3,
    },
    {
        date: "2023-06-02",
        Temperatures: 19,
        Humidity: 74.6,
        UV_index: 7,
    },
    {
        date: "2023-06-03",
        Temperatures: 23,
        Humidity: 80,
        UV_index: 9,
    },
    {
        date: "2023-06-04",
        Temperatures: 16,
        Humidity: 90.2,
        UV_index: 4,
    },
    {
        date: "2023-06-05",
        Temperatures: 15,
        Humidity: 87,
        UV_index: 2,
    },
    {
        date: "2023-06-06",
        Temperatures: 16,
        Humidity: 76.2,
        UV_index: 4,
    },
    {
        date: "2023-06-07",
        Temperatures: 20,
        Humidity: 86.5,
        UV_index: 2,
    },
    {
        date: "2023-06-08",
        Temperatures: 18,
        Humidity: 82.2,
        UV_index: 6,
    },
    {
        date: "2023-06-09",
        Temperatures: 16,
        Humidity: 76.2,
        UV_index: 5.5,
    },
];

export default function ChartView() {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const selectedKpi = kpiList[selectedIndex];

    const areaChartArgs = {
        className: "mt-5 h-72",
        data: performance,
        index: "date",
        categories: [selectedKpi],
        colors: ["blue"] as Color[],
        showLegend: false,
        valueFormatter: formatters[selectedKpi],
        yAxisWidth: 56,
    };

    return (
        <>
            <div className="md:flex justify-between">
                <div>
                    <Flex className="space-x-0.5" justifyContent="start" alignItems="center">
                        <Title> Sensors History </Title>
                        <Icon
                            icon={InformationCircleIcon}
                            variant="simple"
                            tooltip="Shows daily increase or decrease of particular domain"
                        />
                    </Flex>
                    <Text> Average daily change per domain </Text>
                </div>
                <div>
                    <TabGroup index={selectedIndex} onIndexChange={setSelectedIndex}>
                        <TabList color="gray" variant="solid">
                            <Tab>Temperatures</Tab>
                            <Tab>Humidity</Tab>
                            <Tab>UV_index</Tab>
                        </TabList>
                    </TabGroup>
                </div>
            </div>
            {/* web */}
            <div className="mt-8 hidden sm:block">
                <AreaChart {...areaChartArgs} />
            </div>
            {/* mobile */}
            <div className="mt-8 sm:hidden">
                <AreaChart {...areaChartArgs} startEndOnly={true} showGradient={false} showYAxis={false} />
            </div>
        </>
    );
}
