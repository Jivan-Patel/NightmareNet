// frontend/src/__tests__/SettingsPanel.test.tsx
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";

// Mock framer-motion to avoid animation complexity in tests
vi.mock("framer-motion", () => {
    const createMotionMock = (tag: string) =>
        function MockMotionComponent(props: Record<string, unknown>) {
            const {
                children,
                whileHover,
                whileTap,
                initial,
                animate,
                exit,
                transition,
                variants,
                layout,
                ref,
                ...domProps
            } = props;
            void whileHover; void whileTap; void initial; void animate;
            void exit; void transition; void variants; void layout;
            return React.createElement(tag, { ...domProps, ref }, children as React.ReactNode);
        };

    return {
        motion: new Proxy({}, { get: (_t, prop: string) => createMotionMock(prop) }),
        AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
        HTMLMotionProps: {},
    };
});

// Mock useSounds hook
vi.mock("@/lib/sounds", () => ({
    useSounds: () => ({
        playClick: vi.fn(),
        playSuccess: vi.fn(),
        playError: vi.fn(),
        playTransition: vi.fn(),
        playNotification: vi.fn(),
        enabled: true,
        toggle: vi.fn(),
    }),
}));

// Use vi.hoisted so these are defined before vi.mock is hoisted above them
const { pushMock, testWebhookMock } = vi.hoisted(() => ({
    pushMock: vi.fn(),
    testWebhookMock: vi.fn(),
}));

// Mock useToast hook
vi.mock("@/components/ui/Toast", () => ({
    useToast: () => ({ push: pushMock }),
}));

// Mock the webhook API call — we don't want real network requests in tests
vi.mock("@/lib/api", () => ({
    testWebhook: (...args: unknown[]) => testWebhookMock(...args),
}));

import { SettingsPanel } from "@/components/dashboard/SettingsPanel";

describe("SettingsPanel component", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    it("renders without crashing, defaulting to the API Keys tab", () => {
        render(<SettingsPanel />);
        expect(screen.getByText("API Keys")).toBeInTheDocument();
        expect(screen.getByText("Generate key")).toBeInTheDocument();
    });

    it("shows the seeded webhook URL on the Notifications tab", () => {
        render(<SettingsPanel />);
        fireEvent.click(screen.getByText("Notifications"));
        expect(
            screen.getByPlaceholderText("https://hooks.slack.com/services/...")
        ).toBeInTheDocument();
    });

    it("shows the empty state after removing the only webhook", () => {
        render(<SettingsPanel />);
        fireEvent.click(screen.getByText("Notifications"));
        fireEvent.click(screen.getByText("Remove"));
        expect(screen.getByText(/No webhooks configured/i)).toBeInTheDocument();
    });

    it("adds a second empty webhook row when Add Webhook is clicked", () => {
        render(<SettingsPanel />);
        fireEvent.click(screen.getByText("Notifications"));
        fireEvent.click(screen.getByText("Add Webhook"));
        expect(
            screen.getAllByPlaceholderText("https://hooks.slack.com/services/...")
        ).toHaveLength(2);
    });

    it("shows a success toast when the webhook test succeeds", async () => {
        testWebhookMock.mockResolvedValueOnce({ status: "success" });
        render(<SettingsPanel />);
        fireEvent.click(screen.getByText("Notifications"));
        fireEvent.click(screen.getByText("Test Connection"));

        await waitFor(() => expect(testWebhookMock).toHaveBeenCalled());
        await waitFor(() =>
            expect(pushMock).toHaveBeenCalledWith(
                expect.objectContaining({ title: "Webhook Verified" })
            )
        );
    });

    it("shows an error toast when the webhook test fails", async () => {
        testWebhookMock.mockRejectedValueOnce(new Error("Connection refused"));
        render(<SettingsPanel />);
        fireEvent.click(screen.getByText("Notifications"));
        fireEvent.click(screen.getByText("Test Connection"));

        await waitFor(() =>
            expect(pushMock).toHaveBeenCalledWith(
                expect.objectContaining({
                    title: "Connection Failed",
                    description: "Connection refused",
                })
            )
        );
    });
});